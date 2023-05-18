from utils.starktrack.lib.test.utils import TrackerParams
import os
from utils.starktrack.lib.test.evaluation.environment import env_settings
from utils.starktrack.lib.config.stark_s.config import cfg, update_config_from_file


def parameters(yaml_name: str):
    params = TrackerParams()
    # prj_dir = env_settings().prj_dir
    # save_dir = env_settings().save_dir
    # update default config from yaml file
    # yaml_file = os.path.join(prj_dir, 'experiments/stark_s/%s.yaml' % yaml_name)
    update_config_from_file(yaml_name)
    params.cfg = cfg
    print("test config: ", cfg)

    # template and search region
    params.template_factor = cfg.TEST.TEMPLATE_FACTOR
    params.template_size = cfg.TEST.TEMPLATE_SIZE
    params.search_factor = cfg.TEST.SEARCH_FACTOR
    params.search_size = cfg.TEST.SEARCH_SIZE

    # Network checkpoint path
    params.checkpoint = 'model/tracking/stark/STARKS_ep0500.pth.tar'

    # whether to save boxes from all queries
    params.save_all_boxes = False

    return params
