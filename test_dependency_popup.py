#!/usr/bin/env python3
"""Test dependency popup directly."""

import sys
import ttkbootstrap as ttk
from reader_gui.dependency_check import DependencyPopup

def test_popup():
    """Test the dependency popup in isolation."""
    print("Creating test window...")
    root = ttk.Window(themename='darkly', title="Test Parent Window")
    root.geometry("400x300")

    # Add a label so we can see the parent window
    ttk.Label(
        root,
        text="Parent Window\n(Should stay visible while popup shows)",
        font=("Monaco", 14)
    ).pack(expand=True)

    def show_popup():
        """Show the dependency popup."""
        print("Creating DependencyPopup...")
        try:
            popup = DependencyPopup(root, ['ffmpeg', 'model'])
            print(f"Popup created: {popup}")
            print(f"Popup parent: {popup.parent}")
            print(f"Popup is visible: {popup.winfo_viewable()}")
            print("Waiting for popup to close...")
            root.wait_window(popup)
            print("Popup closed")
        except Exception as e:
            print(f"ERROR creating popup: {e}")
            import traceback
            traceback.print_exc()

    # Show popup after a delay so we can see the parent window first
    root.after(1000, show_popup)

    print("Starting mainloop...")
    root.mainloop()
    print("Mainloop exited")

if __name__ == "__main__":
    test_popup()
