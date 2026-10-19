"""Camera-specific ROI -> resumable annotation review; no automatic test scoring."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import threading
import time
from types import SimpleNamespace
import uuid

from code.scripts import gt_newcam
from code.scripts.gt_mixed_app import MixedReviewApp
from code.scripts.gt_mixed_review import MixedStore
from code.scripts.gt_roi import load_roi

LABELS = {'duongbatrac_0800': 'Dương Bá Trạc', 'conghoa_uttich_1715': 'Cộng Hòa – Út Tịch',
          'conghoa_truongchinh_1700': 'Cộng Hòa – Trường Chinh'}


def check_parent(camera):
    if camera not in gt_newcam.CAMERAS:
        raise ValueError('Unknown camera')
    parent = gt_newcam.parent_bundle(camera)
    store = MixedStore(parent)
    store.check_inputs(images=True)
    window = json.loads((gt_newcam.ROOT/camera/'window.json').read_text(encoding='utf8'))
    if store.manifest['segment'] != [window['start'], window['end']]:
        raise ValueError('Camera window and annotation bundle disagree')
    if store.manifest['n_frames'] != window['end']-window['start']:
        raise ValueError('Incomplete camera window')
    return parent


def prepare_review(camera, progress=print):
    """Isolated ROI child; never replace the parent's decisions or Mixed pointer."""
    parent = check_parent(camera)
    roi = load_roi(parent)
    if not roi or not roi['enabled']:
        raise ValueError('Draw and save an enabled ROI for this camera first')
    gt_newcam.scope(camera)
    child = gt_newcam.roi_child(camera)
    store = MixedStore(child)
    store.check_inputs(images=True)
    if store.manifest.get('review_scope') != 'ROI_ONLY':
        raise ValueError('A scoped ROI review is required')
    if progress:
        progress(f'Đã sẵn sàng: {len(store.rows)} mục; còn {store.tally["PENDING"]} mục chưa duyệt.')
    return child


def export_review(camera, bundle, reviewer, progress=None):
    """Versioned export only. Missing reviews/frame coverage fail inside finalize."""
    version = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
    output = gt_newcam.ROOT/camera/'reviewed'/version
    if progress:
        progress('Đang kiểm tra và lưu GT camera mới…')
    return gt_newcam.finalize(camera, reviewer, det='best_640', evaluate=False,
                             out_dir=output, expected_bundle=bundle)


class NewCameraReviewApp(MixedReviewApp):
    finish_status = 'Đang kiểm tra và lưu GT camera mới…'
    busy_close_message = 'Đợi lưu GT xong trước khi đóng.'

    def __init__(self, root, args):
        self.segment_label = LABELS[args.camera]
        self.activity_path = Path(args.bundle)/'review_activity.jsonl'
        self.case_started = time.perf_counter()
        super().__init__(root, args)
        self.finish_button.configure(text='Hoàn tất → lưu GT camera mới')
        self.status.set('Mỗi lựa chọn và sửa box được tự lưu. Có thể đóng và mở lại bằng review_gt_duongbatrac.cmd.')

    def check_store(self, store):
        super().check_store(store)
        self.window_title = f'CAAP — {LABELS[self.args.camera]} · GT trong ROI · Nghĩa review'

    def show(self):
        self.case_started = time.perf_counter()
        super().show()

    def save_note(self, decision=None):
        old = self.store.rows[self.index]['decision']
        saved = super().save_note(decision)
        new = self.store.rows[self.index]['decision']
        if saved and new and old != new:
            # Timing aid only: includes idle time, never treated as active labour.
            record = dict(utc=datetime.now(timezone.utc).isoformat(),
                          rank=self.store.rows[self.index]['rank'],
                          kind=self.store.rows[self.index]['kind'], decision=new,
                          elapsed_wall_seconds=time.perf_counter()-self.case_started,
                          timing_scope='wall time since case display; includes idle and video editing')
            try:
                with self.activity_path.open('a', encoding='utf8') as stream:
                    stream.write(json.dumps(record, ensure_ascii=False)+'\n')
            except OSError:
                self.status.set('Quyết định đã lưu; nhật ký thời gian không ghi được.')
        return saved

    def roi_editor(self):
        from tkinter import messagebox
        messagebox.showinfo('ROI đã chốt',
            'Muốn đổi vùng, đóng cửa sổ và chạy review_gt_duongbatrac.cmd --edit-roi. '
            'Công cụ sẽ tạo phiên riêng và giữ tiến độ cũ.', parent=self.root)

    def run_finalize(self, reviewer, progress):
        return export_review(self.args.camera, self.args.bundle, reviewer, progress)

    def completion_message(self, result):
        return f'GT camera mới đã lưu tại:\n{result}\n\nBạn đã hoàn tất lượt review. Bước chấm điểm được thực hiện riêng sau khi khóa protocol.'


def launch(camera, reviewer='Nghĩa', edit_roi=False):
    import tkinter as tk
    from tkinter import messagebox, ttk
    from code.scripts.gt_roi_app import ROIEditor
    parent = check_parent(camera)
    roi = load_roi(parent)
    if edit_roi or roi is None or not roi['enabled']:
        root = tk.Tk()
        editor = ROIEditor(root, parent, reviewer)
        root.title(f'CAAP — {LABELS[camera]} · Bước 1: chọn ROI')
        if roi is None:
            editor.reason.set('Chỉ gán nhãn trong vùng nhìn rõ xe và phân biệt được ID.')
        editor.status.set('Khoanh vùng nhìn rõ xe. Điền lý do, bấm Lưu ROI, rồi bấm Đóng để sang bước review.')
        root.mainloop()
        roi = load_roi(parent)
        if roi is None or not roi['enabled']:
            return  # Closing without an enabled saved ROI never invents a scope.

    loading = tk.Tk()
    loading.title(f'CAAP — {LABELS[camera]} · Chuẩn bị review')
    loading.geometry('580x130')
    ttk.Label(loading, text='Đang tạo hàng chờ trong ROI. Giữ cửa sổ này mở…', padding=14).pack()
    bar = ttk.Progressbar(loading, mode='indeterminate');bar.pack(fill='x', padx=14);bar.start()
    events = queue.Queue()
    result = {}
    def worker():
        try:
            events.put((True, prepare_review(camera)))
        except Exception as error:
            events.put((False, str(error)))
    def poll():
        try:
            success, value = events.get_nowait()
        except queue.Empty:
            loading.after(150, poll)
            return
        if success:
            result['bundle'] = value
        else:
            messagebox.showerror('Chưa mở được review', value, parent=loading)
        loading.destroy()
    loading.protocol('WM_DELETE_WINDOW', lambda: messagebox.showinfo('Đang chuẩn bị', 'Đợi tạo phiên review xong trước khi đóng.', parent=loading))
    threading.Thread(target=worker, daemon=True).start()
    loading.after(150, poll)
    loading.mainloop()
    if 'bundle' not in result:
        raise RuntimeError('Camera review preparation failed; see the error above')
    root = tk.Tk()
    args = SimpleNamespace(camera=camera, bundle=result['bundle'], reviewer=reviewer,
                           tracks_dir=gt_newcam.dumps_dir(camera, 'best_640'))
    NewCameraReviewApp(root, args)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--camera', choices=list(gt_newcam.CAMERAS), default='duongbatrac_0800')
    parser.add_argument('--reviewer', default='Nghĩa')
    parser.add_argument('--edit-roi', action='store_true')
    parser.add_argument('--prepare-only', action='store_true', help='Prepare a saved ROI without opening windows')
    args = parser.parse_args()
    if args.prepare_only:
        print(prepare_review(args.camera))
    else:
        launch(args.camera, args.reviewer, args.edit_roi)


if __name__ == '__main__':
    main()
