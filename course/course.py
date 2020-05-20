import os
import pandas as pd
from pathlib import Path
import numpy as np
from scripts.bm_experiments.generate_regist_pairs import main as generate
from scripts.bm_experiments.bm_bUnwarpJ import BmUnwarpJ
from scripts.bm_experiments.bm_RVSS import BmRVSS
import sys

def int_keypoints(dataset_path):
    """Keypoints conversion

    Parameters
    ----------
    dataset_path: string
        Path of the dataset
    Returns
    -------
       Converts float keypoints to int and deletes spaces
    """
    
    for dirpath, dirnames, filenames in os.walk(dataset_path):

        for filename in filenames:
            if Path(filename).suffix == '.csv':
                table = pd.read_csv(os.path.join(dirpath, filename))
                table.X = round(table.X).astype(np.int64)
                table.Y = round(table.Y).astype(np.int64)
                file, file_extension = os.path.splitext(os.path.join(dirpath, filename))
                table.to_csv(file.replace(" ", "") + "_int.csv", index=False)
                if not os.path.exists(os.path.join(dirpath,"old")):
                    os.mkdir(os.path.join(dirpath, "old"))
                os.replace(os.path.join(dirpath, filename), os.path.join(dirpath, 'old', filename))


def create_dataset_table(dataset_path, output_csv, image_format, mode="first2all"):
    """Table creation

    Parameters
    ----------
    dataset_path: string
        Path of the dataset
    output_csv: string
        Path of the output file (with it's name)
    image_format: string
        Format of the image (Ex.: jpg, png, tiff)
    mode:
        first2all - registering the first image to all others
        each2all -  registering each image to all other
    Returns
    -------
        Creates csv table for each dataset sample
    """
    image_format = "." + image_format

    for dirpath, dirnames, filenames in os.walk(dataset_path):

        suffix = [Path(i).suffix for i in filenames]
        if ".csv" in suffix and image_format in suffix:
            img_path = os.path.abspath(dirpath)+"/*"+image_format
            csv_path = os.path.abspath(dirpath)+"/*.csv"
            output = dirpath+"/"+output_csv
            generate(img_path, csv_path, output, mode)


def Transformation(type, csv_name, dataset_path, config_path, ImageJ_path, output_path="general"):
    """FFD transformation
    !This method requires manual installation of ImageJ!
    Parameters
    ----------
    type: string
        Type of the transformation: linear or B-spline
    csv_name: string
        Name  of the csv registering table.
        For each sample names must identical
        Ex.: csv_table.csv
    dataset_path: string
        Path of the dataset
    config_path:
        Path of the bUnwarpJ configuration
    ImageJ_path:
        Path of the ImageJ application
    output_path: string
        Path of the results:
            unique - place results in sample path
            general - place results in dataset path
            other - place results in user path

    Returns
    -------
        performs transformation
    """
    if output_path == "general":
        output_path = dataset_path

    params = {'path_table': 0, 'path_out': output_path, 'exec_Fiji': ImageJ_path, 'path_dataset': 0,
              'unique': True, 'visual': True, 'path_config': config_path, "run_comp_benchmark": False}

    for dirpath, dirnames, filenames in os.walk(dataset_path):

        if csv_name in filenames:
            params['path_table'] = os.path.join(os.path.abspath(dirpath),csv_name)
            params['path_dataset'] = os.path.abspath(dirpath)
            if output_path == "unique":
                params['path_out'] = os.path.abspath(dirpath)
            if type == "B-spline":
                benchmark = BmUnwarpJ(params)
                benchmark.run()
            else:
                benchmark = BmRVSS(params)
                benchmark.run()
            del benchmark

if __name__ == '__main__':

    if len(sys.argv) > 2:
        globals()[sys.argv[1]](*[sys.argv[i] for i in range(2, len(sys.argv))])






