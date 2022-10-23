class HELPERS:
    def get_size(bytes):
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes <= 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024