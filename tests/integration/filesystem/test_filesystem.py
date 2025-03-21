"""
Integration tests for filesystem operations.
"""
import pytest
import os
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from core.filesystem import FilesystemHandler

@pytest.mark.integration
class TestFilesystemOperations:
    """Integration test suite for filesystem operations."""
    
    @pytest.fixture
    def fs_handler(self, tmp_path):
        """Fixture to provide a filesystem handler instance."""
        handler = FilesystemHandler(base_path=tmp_path)
        return handler
        
    @pytest.fixture
    def test_dir(self, tmp_path):
        """Fixture to provide a test directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        return test_dir
        
    @pytest.fixture
    def test_file(self, test_dir):
        """Fixture to provide a test file."""
        test_file = test_dir / "test.txt"
        test_file.write_text("Test content")
        return test_file
        
    async def test_file_operations(self, fs_handler, test_dir):
        """Test basic file operations."""
        # Setup
        file_path = test_dir / "file_ops.txt"
        content = "Test file content"
        
        # Test write
        await fs_handler.write_file(file_path, content)
        assert file_path.exists()
        
        # Test read
        read_content = await fs_handler.read_file(file_path)
        assert read_content == content
        
        # Test append
        append_content = "\nAppended content"
        await fs_handler.append_file(file_path, append_content)
        updated_content = await fs_handler.read_file(file_path)
        assert updated_content == content + append_content
        
        # Test delete
        await fs_handler.delete_file(file_path)
        assert not file_path.exists()
        
    async def test_directory_operations(self, fs_handler, test_dir):
        """Test directory operations."""
        # Setup
        new_dir = test_dir / "new_dir"
        
        # Test create directory
        await fs_handler.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()
        
        # Test list directory
        test_file = new_dir / "test.txt"
        test_file.write_text("Test content")
        
        contents = await fs_handler.list_directory(new_dir)
        assert "test.txt" in contents
        
        # Test delete directory
        await fs_handler.delete_directory(new_dir)
        assert not new_dir.exists()
        
    async def test_json_operations(self, fs_handler, test_dir):
        """Test JSON file operations."""
        # Setup
        json_path = test_dir / "test.json"
        test_data = {
            "name": "Test",
            "value": 123,
            "nested": {
                "key": "value"
            }
        }
        
        # Test write JSON
        await fs_handler.write_json(json_path, test_data)
        assert json_path.exists()
        
        # Test read JSON
        read_data = await fs_handler.read_json(json_path)
        assert read_data == test_data
        
        # Test update JSON
        update_data = {"value": 456}
        await fs_handler.update_json(json_path, update_data)
        updated_data = await fs_handler.read_json(json_path)
        assert updated_data["value"] == 456
        assert updated_data["name"] == test_data["name"]
        
    async def test_yaml_operations(self, fs_handler, test_dir):
        """Test YAML file operations."""
        # Setup
        yaml_path = test_dir / "test.yaml"
        test_data = {
            "config": {
                "server": "localhost",
                "port": 8080,
                "settings": {
                    "debug": True,
                    "timeout": 30
                }
            }
        }
        
        # Test write YAML
        await fs_handler.write_yaml(yaml_path, test_data)
        assert yaml_path.exists()
        
        # Test read YAML
        read_data = await fs_handler.read_yaml(yaml_path)
        assert read_data == test_data
        
        # Test update YAML
        update_data = {"config": {"port": 9090}}
        await fs_handler.update_yaml(yaml_path, update_data)
        updated_data = await fs_handler.read_yaml(yaml_path)
        assert updated_data["config"]["port"] == 9090
        assert updated_data["config"]["server"] == test_data["config"]["server"]
        
    async def test_file_search(self, fs_handler, test_dir):
        """Test file search operations."""
        # Setup
        for i in range(3):
            file_path = test_dir / f"test{i}.txt"
            file_path.write_text(f"Content {i}")
            
        # Test search by pattern
        txt_files = await fs_handler.find_files(test_dir, "*.txt")
        assert len(txt_files) == 3
        
        # Test search by content
        content_files = await fs_handler.search_files(test_dir, "Content 1")
        assert len(content_files) == 1
        
    async def test_file_attributes(self, fs_handler, test_file):
        """Test file attribute operations."""
        # Test get attributes
        attrs = await fs_handler.get_file_attributes(test_file)
        assert "size" in attrs
        assert "created" in attrs
        assert "modified" in attrs
        assert "permissions" in attrs
        
        # Test set attributes
        new_perms = 0o644
        await fs_handler.set_file_permissions(test_file, new_perms)
        updated_attrs = await fs_handler.get_file_attributes(test_file)
        assert oct(updated_attrs["permissions"])[-3:] == oct(new_perms)[-3:]
        
    async def test_file_copy_move(self, fs_handler, test_dir, test_file):
        """Test file copy and move operations."""
        # Setup
        dest_dir = test_dir / "dest"
        dest_dir.mkdir()
        
        # Test copy file
        copy_path = dest_dir / test_file.name
        await fs_handler.copy_file(test_file, copy_path)
        assert copy_path.exists()
        assert test_file.exists()
        
        # Test move file
        move_path = dest_dir / "moved.txt"
        await fs_handler.move_file(test_file, move_path)
        assert move_path.exists()
        assert not test_file.exists()
        
    async def test_directory_copy_move(self, fs_handler, test_dir):
        """Test directory copy and move operations."""
        # Setup
        source_dir = test_dir / "source"
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("Test content")
        
        dest_parent = test_dir / "dest"
        dest_parent.mkdir()
        
        # Test copy directory
        copy_dir = dest_parent / "copy"
        await fs_handler.copy_directory(source_dir, copy_dir)
        assert copy_dir.exists()
        assert (copy_dir / "test.txt").exists()
        assert source_dir.exists()
        
        # Test move directory
        move_dir = dest_parent / "moved"
        await fs_handler.move_directory(source_dir, move_dir)
        assert move_dir.exists()
        assert (move_dir / "test.txt").exists()
        assert not source_dir.exists()
        
    async def test_file_watching(self, fs_handler, test_dir):
        """Test file watching operations."""
        # Setup
        watch_file = test_dir / "watched.txt"
        watch_file.write_text("Initial content")
        
        # Start watching
        events = []
        async def callback(event):
            events.append(event)
            
        await fs_handler.watch_file(watch_file, callback)
        
        # Modify file
        watch_file.write_text("Modified content")
        await asyncio.sleep(1)  # Wait for event
        
        # Stop watching
        await fs_handler.stop_watching(watch_file)
        
        assert len(events) > 0
        assert events[0]["type"] == "modified"
        
    async def test_directory_watching(self, fs_handler, test_dir):
        """Test directory watching operations."""
        # Setup
        watch_dir = test_dir / "watched"
        watch_dir.mkdir()
        
        # Start watching
        events = []
        async def callback(event):
            events.append(event)
            
        await fs_handler.watch_directory(watch_dir, callback)
        
        # Create file
        new_file = watch_dir / "new.txt"
        new_file.write_text("New content")
        await asyncio.sleep(1)  # Wait for event
        
        # Stop watching
        await fs_handler.stop_watching(watch_dir)
        
        assert len(events) > 0
        assert events[0]["type"] == "created"
        
    async def test_file_locking(self, fs_handler, test_file):
        """Test file locking operations."""
        # Test acquire lock
        async with await fs_handler.lock_file(test_file):
            # Verify file is locked
            assert await fs_handler.is_file_locked(test_file)
            
            # Try to modify file
            content = "Modified while locked"
            await fs_handler.write_file(test_file, content)
            
        # Verify lock is released
        assert not await fs_handler.is_file_locked(test_file)
        
    async def test_temporary_files(self, fs_handler):
        """Test temporary file operations."""
        # Test create temporary file
        temp_file = await fs_handler.create_temp_file()
        assert temp_file.exists()
        
        # Write content
        content = "Temporary content"
        await fs_handler.write_file(temp_file, content)
        
        # Read content
        read_content = await fs_handler.read_file(temp_file)
        assert read_content == content
        
        # Cleanup
        await fs_handler.delete_file(temp_file)
        assert not temp_file.exists()
        
    async def test_error_handling(self, fs_handler, test_dir):
        """Test filesystem error handling."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            await fs_handler.read_file(test_dir / "nonexistent.txt")
            
        # Test permission error
        no_access_dir = test_dir / "no_access"
        no_access_dir.mkdir()
        no_access_dir.chmod(0o000)
        
        with pytest.raises(PermissionError):
            await fs_handler.create_directory(no_access_dir / "subdir")
            
        # Cleanup
        no_access_dir.chmod(0o755)
        await fs_handler.delete_directory(no_access_dir)
        
    async def test_path_operations(self, fs_handler, test_dir):
        """Test path manipulation operations."""
        # Test path joining
        path = await fs_handler.join_paths(test_dir, "subdir", "file.txt")
        assert str(path) == str(test_dir / "subdir" / "file.txt")
        
        # Test path resolution
        relative_path = "./test/../test/file.txt"
        resolved_path = await fs_handler.resolve_path(test_dir / relative_path)
        assert str(resolved_path) == str(test_dir / "file.txt")
        
        # Test path existence
        assert await fs_handler.path_exists(test_dir)
        assert not await fs_handler.path_exists(test_dir / "nonexistent") 