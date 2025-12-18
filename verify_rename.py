import os
import shutil
import unittest
from unittest.mock import MagicMock, patch
import sys

# Add current directory to path so we can import batch_rename
sys.path.append(os.getcwd())
import batch_rename

class TestBatchRename(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_rename_folder"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create dummy images
        self.files = ["a.jpg", "b.png", "c.WRONG", "d.webp"]
        for f in self.files:
            with open(os.path.join(self.test_dir, f), 'w') as fh:
                fh.write("dummy content")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('batch_rename.messagebox')
    def test_renaming_jpg_only(self, mock_mb):
        # Mock status callback
        mock_callback = MagicMock()
        
        # Run renaming for JPG only
        allowed = {'.jpg', '.jpeg'}
        batch_rename.rename_images_in_folder(os.path.abspath(self.test_dir), allowed, mock_callback)
        
        # Check results
        files_after = os.listdir(self.test_dir)
        files_after.sort()
        
        # Expected: 
        # a.jpg -> test_rename_folder_1.jpg
        # b.png -> b.png (ignored)
        # c.WRONG -> c.WRONG (ignored)
        # d.webp -> d.webp (ignored)
        
        expected = [
            "b.png",
            "c.WRONG", 
            "d.webp",
            "test_rename_folder_1.jpg"
        ]
        expected.sort()
        
        print("\nFiles after rename (JPG only):", files_after)
        
        self.assertEqual(files_after, expected)
        
        # Verify messagebox success called
        self.assertTrue(mock_mb.showinfo.called)

if __name__ == '__main__':
    unittest.main()
