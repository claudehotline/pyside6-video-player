_base_ = [
    '../_base_/datasets/ccpd2019.py',
    '../_base_/datasets/ccpd2020.py',
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_adam_step_5e.py',
    '_base_sar_resnet31_parallel-decoder.py',
]

default_hooks = dict(logger=dict(type='LoggerHook', interval=100))

# dataset settings
train_list = [
    _base_.ccpd2019_textrecog_train, _base_.ccpd2020_textrecog_train
]

test_list = [
    _base_.ccpd2019_textrecog_val, _base_.ccpd2020_textrecog_val
]

# train_list = [
#     # dict(
#     #     type='RepeatDataset',
#     #     dataset=dict(
#     #         type='ConcatDataset',
#     #         datasets=train_list[:2],
#     #         pipeline=_base_.train_pipeline),
#     #     times=20),
#     dict(
#         type='ConcatDataset',
#         datasets=train_list[5:],
#         pipeline=_base_.train_pipeline),
# ]
train_dataset = dict(
    type='ConcatDataset', datasets=train_list, pipeline=_base_.train_pipeline)
test_dataset = dict(
       type='ConcatDataset', datasets=test_list, pipeline=_base_.test_pipeline)

train_dataloader = dict(
    batch_size=64,
    num_workers=24,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=train_dataset
)

test_dataloader = dict(
    batch_size=1,
    num_workers=4,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=test_dataset
)

# train_dataloader = dict(
#     batch_size=64 * 6,
#     num_workers=24,
#     persistent_workers=True,
#     sampler=dict(type='DefaultSampler', shuffle=True),
#     dataset=dict(type='ConcatDataset', datasets=train_list, verify_meta=False))
# test_dataloader = dict(
#     batch_size=1,
#     num_workers=4,
#     persistent_workers=True,
#     drop_last=False,
#     sampler=dict(type='DefaultSampler', shuffle=False),
#     dataset=dict(
#         type='ConcatDataset',
#         datasets=test_list,
#         pipeline=_base_.test_pipeline))
val_dataloader = test_dataloader

# val_evaluator = dict(
#     dataset_prefixes=['CCPD2019', 'CCPD2020'])
# test_evaluator = val_evaluator

auto_scale_lr = dict(base_batch_size=64 * 48)
