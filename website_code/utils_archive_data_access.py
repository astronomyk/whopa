import os

def build_file_tree(root_dir):
    tree = []
    for foldername in sorted(os.listdir(root_dir)):
        folder_path = os.path.join(root_dir, foldername)
        if os.path.isdir(folder_path):
            files = []
            for filename in sorted(os.listdir(folder_path)):
                file_path = os.path.join(foldername, filename)
                files.append({
                    "name": filename,
                    "path": file_path
                })
            tree.append({
                "name": foldername,
                "files": files
            })
    return tree
