class EnvironmentSettings:
    def __init__(self):
        self.workspace_dir = '/content/Stark'    # Base directory for saving network checkpoints.
        self.tensorboard_dir = '/content/Stark/tensorboard'    # Directory for tensorboard files.
        self.pretrained_networks = '/content/Stark/pretrained_networks'
        self.lasot_dir = '/content/Stark/data/lasot'
        self.got10k_dir = '/content/Stark/data/got10k'
        self.lasot_lmdb_dir = '/content/Stark/data/lasot_lmdb'
        self.got10k_lmdb_dir = '/content/Stark/data/got10k_lmdb'
        self.trackingnet_dir = '/content/Stark/data/trackingnet'
        self.trackingnet_lmdb_dir = '/content/Stark/data/trackingnet_lmdb'
        self.coco_dir = '/content/Stark/data/coco'
        self.coco_lmdb_dir = '/content/Stark/data/coco_lmdb'
        self.lvis_dir = ''
        self.sbd_dir = ''
        self.imagenet_dir = '/content/Stark/data/vid'
        self.imagenet_lmdb_dir = '/content/Stark/data/vid_lmdb'
        self.imagenetdet_dir = ''
        self.ecssd_dir = ''
        self.hkuis_dir = ''
        self.msra10k_dir = ''
        self.davis_dir = ''
        self.youtubevos_dir = ''
