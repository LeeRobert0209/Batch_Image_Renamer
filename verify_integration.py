
import os
import shutil
import unittest
from src.core.renamer import RenamerEngine
from src.core.file_ops import FileProcessor

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_env"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.files = ["img1.jpg", "img2.PNG", "readme.txt"]
        for f in self.files:
            with open(os.path.join(self.test_dir, f), 'w') as fh:
                fh.write("datum")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_sequence_rename_and_undo(self):
        # 1. Setup Engine
        engine = RenamerEngine()
        processor = FileProcessor()
        
        file_paths = [os.path.join(self.test_dir, f) for f in self.files if f.endswith(('.jpg', '.PNG'))]
        
        # 2. Set Rules (Prefix=Photo, Start=10)
        rules = {
            'mode': 'sequence',
            'prefix': 'Photo',
            'start_index': 10,
            'padding': 3,
            'case': 'lower'
        }
        engine.set_rules(rules)
        
        # 3. Generate Preview
        preview = engine.generate_preview(file_paths)
        
        # Expected: img1.jpg -> photo_010.jpg, img2.PNG -> photo_011.png
        # Note: img2.PNG extension becomes .png if we lowercased logic correctly in renamer
        
        # 4. Execute
        count, err = processor.execute_rename(preview)
        self.assertEqual(count, 2)
        
        # Verify files on disk
        current_files = os.listdir(self.test_dir)
        self.assertIn("photo_010.jpg", current_files)
        self.assertIn("photo_011.png", current_files)
        self.assertIn("readme.txt", current_files) # Should be untouched
        
        print("Rename Success. Current files:", current_files)
        
        # 5. Undo
        count_undo, err_undo = processor.undo_last_operation()
        self.assertEqual(count_undo, 2)
        
        # Verify Revert
        restored_files = os.listdir(self.test_dir)
        self.assertIn("img1.jpg", restored_files)
        self.assertIn("img2.PNG", restored_files)
        
        print("Undo Success. Files restored:", restored_files)

    def test_regex_rename(self):
        engine = RenamerEngine()
        file_paths = [os.path.join(self.test_dir, "img1.jpg")]
        
        rules = {
            'mode': 'regex',
            'regex_pattern': r'img(\d+)',
            'regex_replacement': r'Picture-\1'
        }
        engine.set_rules(rules)
        preview = engine.generate_preview(file_paths)
        
        # Expected: img1.jpg -> Picture-1.jpg
        self.assertEqual(preview[0]['new'], "Picture-1.jpg")
        print("Regex Preview Success:", preview[0]['new'])

if __name__ == '__main__':
    unittest.main()
