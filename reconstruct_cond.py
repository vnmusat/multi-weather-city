from glob import glob
import os
import cv2
import numpy as np
import argparse


def resize_city(cityscapes_path, multi_weather_city_path):
    all_gt_paths = glob(os.path.join(cityscapes_path,'*','train','*','*.png'),recursive=False)
    for path in all_gt_paths:
        info = path.split(os.path.sep)
        new_path = os.path.join(multi_weather_city_path, 'Cityscapes_overcast', info[-4], info[-3], info[-2], info[-1])
        dir_path = os.path.dirname(new_path)
        gt = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        new_shape = (1024,512)
        if "leftImg8bit.png" in path:
            gt_resized = cv2.resize(gt, new_shape)
        else:
            gt_resized = cv2.resize(gt, new_shape, interpolation=cv2.INTER_NEAREST)
        if len(gt_resized.shape) == 2:
            gt_cropped = gt_resized[:, 256:256+512]
        elif len(gt_resized.shape) == 3:
            gt_cropped = gt_resized[:, 256:256+512, :]
        else:
            raise Exception('Data does not have the right dimensions.')
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                print("Creation of the directory %s failed" % dir_path)
        cv2.imwrite(new_path,gt_cropped)


def reconstruct_condition(img_overcast, img_diff):
    img_recon = img_diff + img_overcast - 255
    img_recon = img_recon.astype(np.uint8)
    return img_recon


def save_recon_img(img_recon, img_recon_path_save):
    dir_path = os.path.dirname(img_recon_path_save)
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            print("Creation of the directory %s failed" % dir_path)
    cv2.imwrite(img_recon_path_save, img_recon)


def get_city_conditions(difference_path_img, mw_city_path):
    all_diff_paths_n = []
    all_diff_paths_nd = []
    all_diff_paths_s = []
    all_diff_paths_sd = []
    all_diff_paths_w = []
    all_diff_paths_wd = []
    all_paths_o = []
    all_diff_paths_od = glob(os.path.join(difference_path_img, 'Cityscapes_overcast_drops', '*', '*', '*', '*.png'))

    for p in all_diff_paths_od:
        all_diff_paths_n.append(p.replace('Cityscapes_overcast_drops','Cityscapes_night'))
        all_diff_paths_nd.append(p.replace('Cityscapes_overcast_drops','Cityscapes_night_drops'))
        all_diff_paths_s.append(p.replace('Cityscapes_overcast_drops','Cityscapes_snow'))
        all_diff_paths_sd.append(p.replace('Cityscapes_overcast_drops','Cityscapes_snow_drops'))
        all_diff_paths_w.append(p.replace('Cityscapes_overcast_drops','Cityscapes_wet'))
        all_diff_paths_wd.append(p.replace('Cityscapes_overcast_drops','Cityscapes_wet_drops'))

    for p in all_diff_paths_od:
        prefix = os.path.join(mw_city_path,'Cityscapes_overcast','leftImg8bit','train')
        info = p.split(os.sep)
        all_paths_o.append(os.path.join(prefix,info[-2],info[-1]))

    save_condition('Cityscapes_overcast_drops', all_paths_o, all_diff_paths_od)
    save_condition('Cityscapes_night', all_paths_o, all_diff_paths_n)
    save_condition('Cityscapes_night_drops', all_paths_o, all_diff_paths_nd)
    save_condition('Cityscapes_snow', all_paths_o, all_diff_paths_s)
    save_condition('Cityscapes_snow_drops', all_paths_o, all_diff_paths_sd)
    save_condition('Cityscapes_wet', all_paths_o, all_diff_paths_w)
    save_condition('Cityscapes_wet_drops', all_paths_o, all_diff_paths_wd)


def save_condition(condition_name, all_paths_o, all_diff_paths_cond):
    for i in range(len(all_paths_o)):
        img_o = cv2.imread(all_paths_o[i], cv2.IMREAD_UNCHANGED).astype(np.uint16)
        img_diff_o_cond = cv2.imread(all_diff_paths_cond[i], cv2.IMREAD_UNCHANGED)
        img_cond = reconstruct_condition(img_o, img_diff_o_cond)
        cond_path = all_paths_o[i].replace('Cityscapes_overcast',condition_name)
        dir_path = os.path.dirname(cond_path)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                print("Creation of the directory %s failed" % dir_path)
        save_recon_img(img_cond, cond_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-cityscapes_path", help="Path to Cityscapes dataset root")
    parser.add_argument("-city_diff_path", help="Path to where all difference images are saved")
    parser.add_argument("-multi_weather_city_path", help="Path to multi weather city root")
    args = parser.parse_args()
    if not os.path.exists(args.multi_weather_city_path):
        try:
            os.makedirs(args.multi_weather_city_path)
        except OSError:
            print("Creation of the directory %s failed" % args.multi_weather_city_path)
    resize_city(args.cityscapes_path, args.multi_weather_city_path)
    get_city_conditions(args.city_diff_path, args.multi_weather_city_path)