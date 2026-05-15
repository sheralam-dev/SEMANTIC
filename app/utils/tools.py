

import struct

def extract_blender_thumbnail(filepath: str):
    """Extracts the embedded PNG thumbnail from a .blend file."""
    try:
        with open(filepath, 'rb') as f:
            # Blender files start with 'BLENDER'
            head = f.read(12)
            if not head.startswith(b'BLENDER'):
                return None

            # Search for the 'REND' (Render) block which holds the thumbnail
            # We read in chunks to find the 'REND' marker
            while True:
                block_head = f.read(24) # Header size for a Blender file block
                if len(block_head) < 24:
                    break
                
                # The first 4 bytes of a block are its ID
                block_id = block_head[:4]
                # Next 4 bytes are the block size (integer)
                block_size = struct.unpack('<I', block_head[4:8])[0]

                if block_id == b'REND':
                    # The REND block contains a 'TEST' header, then dimensions
                    # but the actual PNG data starts shortly after
                    data = f.read(block_size)
                    png_start = data.find(b'\x89PNG')
                    if png_start != -1:
                        return data[png_start:]
                    break
                else:
                    # Skip to the next block
                    f.seek(block_size, 1)
    except Exception as e:
        print(f"Thumbnail error: {e}")
    return None


def get_preview(file_path: str):
    """
    [Quick but Dirty]
    Reads the file, extracts the PNG bytes, and returns them.
    You can then pass these bytes directly to a UI framework 
    (like PyQt, Tkinter, or a web frontend).
    """
    try:
        with open(file_path, 'rb') as f:
            # Read the first 1MB—thumbnails are almost always in this range
            chunk = f.read(1024 * 1024) 
            
            start = chunk.find(b'\x89PNG')
            if start == -1:
                return None
            
            end = chunk.find(b'\xaeB`\x82', start) # Look for the PNG 'IEND' marker
            if end != -1:
                return chunk[start:end + 4]
    except Exception as e:
        print(f"Failed to extract preview: {e}")
    return None
