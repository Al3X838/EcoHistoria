"""
Script to manually compile .po files to .mo files for Flask-Babel
"""
import os
import struct
import array

def generate_mo(po_file, mo_file):
    """Convert a .po file to a .mo file"""
    messages = {}
    current_msgid = None
    current_msgstr = None
    
    with open(po_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                if current_msgid and current_msgstr:
                    messages[current_msgid] = current_msgstr
                    current_msgid = None
                    current_msgstr = None
                continue
            
            # Parse msgid
            if line.startswith('msgid "'):
                if current_msgid and current_msgstr:
                    messages[current_msgid] = current_msgstr
                current_msgid = line[7:-1]  # Remove msgid " and "
                current_msgstr = None
            # Parse msgstr
            elif line.startswith('msgstr "'):
                current_msgstr = line[8:-1]  # Remove msgstr " and "
            # Continuation of previous line
            elif line.startswith('"') and line.endswith('"'):
                text = line[1:-1]
                if current_msgstr is None:
                    current_msgid += text
                else:
                    current_msgstr += text
        
        # Add last message
        if current_msgid and current_msgstr:
            messages[current_msgid] = current_msgstr
    
    # Remove empty key if exists
    if '' in messages:
        del messages['']
    
    # Build .mo file structure
    keys = sorted(messages.keys())
    msg_ids = b''.join([msg.encode('utf-8') + b'\x00' for msg in keys])
    msg_strs = b''.join([messages[msg].encode('utf-8') + b'\x00' for msg in keys])
    
    # Write .mo file
    with open(mo_file, 'wb') as f:
        # Magic number
        f.write(struct.pack('I', 0x950412de))
        # Version
        f.write(struct.pack('I', 0))
        # Number of strings
        f.write(struct.pack('I', len(keys)))
        # Offset of table with original strings
        f.write(struct.pack('I', 28))
        # Offset of table with translation strings  
        f.write(struct.pack('I', 28 + len(keys) * 8))
        # Size of hashing table
        f.write(struct.pack('I', 0))
        # Offset of hashing table
        f.write(struct.pack('I', 0))
        
        # Original strings table
        offset = 28 + len(keys) * 16
        for msg in keys:
            msg_bytes = msg.encode('utf-8') + b'\x00'
            f.write(struct.pack('II', len(msg_bytes) - 1, offset))
            offset += len(msg_bytes)
        
        # Translation strings table
        for msg in keys:
            msg_str_bytes = messages[msg].encode('utf-8') + b'\x00'
            f.write(struct.pack('II', len(msg_str_bytes) - 1, offset))
            offset += len(msg_str_bytes)
        
        # Write actual strings
        f.write(msg_ids)
        f.write(msg_strs)

if __name__ == '__main__':
    # Compile English translations
    po_en = 'translations/en/LC_MESSAGES/messages.po'
    mo_en = 'translations/en/LC_MESSAGES/messages.mo'
    
    if os.path.exists(po_en):
        print(f'Compiling {po_en}...')
        try:
            generate_mo(po_en, mo_en)
            print(f'✓ Created {mo_en}')
        except Exception as e:
            print(f'✗ Error compiling {po_en}: {e}')
    
    # Compile Spanish translations if they exist
    po_es = 'translations/es/LC_MESSAGES/messages.po'
    mo_es = 'translations/es/LC_MESSAGES/messages.mo'
    
    if os.path.exists(po_es):
        print(f'Compiling {po_es}...')
        try:
            generate_mo(po_es, mo_es)
            print(f'✓ Created {mo_es}')
        except Exception as e:
            print(f'✗ Error compiling {po_es}: {e}')
    
    print('\n✅ Translation compilation complete!')

