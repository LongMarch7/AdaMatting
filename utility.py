import torch
import argparse
import logging
import numpy as np


def save_checkpoint(epoch, model, optimizer, cur_iter, max_iter, init_lr, loss, is_best, ckpt_path):
    state = {'epoch': epoch,
             'model': model,
             'optimizer': optimizer,
             'cur_iter': cur_iter,
             'max_iter': max_iter,
             'best_loss': loss,
             'init_lr': init_lr}
    filename = ckpt_path + "ckpt_{:03d}_{:.4f}.tar".format(epoch, loss)
    torch.save(state, filename)
    # If this checkpoint is the best so far, store a copy so it doesn't get overwritten by a worse checkpoint
    if is_best:
        filename = ckpt_path + "ckpt_{:03d}_{:.4f}_best.tar".format(epoch, loss)
        torch.save(state, filename)


def poly_lr_scheduler(optimizer, init_lr, iter, max_iter=100, power=0.9):
    """Polynomial decay of learning rate
        :param init_lr is base learning rate
        :param iter is a current iteration
        :param max_iter is number of maximum iterations
        :param power is a polymomial power

    """
    lr = init_lr * ((1 - iter / max_iter) ** power)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    return lr


class AverageMeter(object):
    """
    Keeps track of the most recent value, average, sum, and count of a metric.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def compute_mse(pred, alpha, trimap):
    """
    compute the MSE error given a prediction, a ground truth and a trimap.
    pred: the predicted alpha matte
    target: the ground truth alpha matte
    trimap: the given trimap
    """
    num_pixels = float((trimap == 128).sum())
    return ((pred - alpha) ** 2).sum() / num_pixels


def compute_sad(pred, alpha):
    """
    compute the SAD error given a prediction and a ground truth.
    """
    diff = np.abs(pred - alpha)
    return np.sum(diff) / 1000


def get_args():
    # Training settings
    parser = argparse.ArgumentParser(description='set arguments')
    parser.add_argument('--mode', type=str, required=True, choices=["train", "test", "prep"], help="set the program to \'train\', \'test\', or \'prep\'")
    parser.add_argument('--valid_portion', type=int, required=True, help="percentage of valid data in all training samples")
    parser.add_argument('--batch_size', type=int, default=64, help='training batch size')
    parser.add_argument('--epochs', type=int, default=20, help='number of epochs to train for')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning Rate. Default=0.01')
    parser.add_argument('--cuda', action='store_true', default=False, help='use cuda?')
    parser.add_argument('--gpu', type=str, default="0", help="choose gpus")
    parser.add_argument('--write_log', action="store_true", default=False, help="whether store log to log.txt")
    parser.add_argument('--raw_data_path', type=str, default="/data/datasets/im/AdaMatting/", help="dir where datasets are stored")
    parser.add_argument('--ckpt_path', type=str, help="path to the saved checkpoint file")
    parser.add_argument('--save_ckpt', action="store_true", default=False, help="whether save checkpoint every 10 epochs")
    parser.add_argument('--resume', action="store_true", default=False, help="whether resume training from a ckpt")
    args = parser.parse_args()
    return args


def get_logger(flag):
    logger = logging.getLogger("AdaMatting")
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(lineno)d: %(levelname)s - %(message)s")

    # log file stream
    if (flag):
        handler = logging.FileHandler("log.txt")
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # log console stream
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger
