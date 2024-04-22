<a name="readme-top"></a>

# Energy impact of image watermarking in serial bus transmission

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <ul>
        <li><a href="#datasets">Datasets</a></li>
        <li><a href="#libraries">Libraries</a></li>
        </ul>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This small project was developed for the "Energy Management for IoT" course (Computer Engineering Master's degree in Embedded Systems at Polytechnic of Turin).\
The objective is to analyze the energy consumption of watermarked images when they are sent over a serial line.

### Built With

#### Datasets
Only a subset of the following datasets has been used to generate the provided simulation results.\
You can find the images in the `images/` folder.

* [DOTA](https://captain-whu.github.io/DOTA/)
* [NuImages](https://www.nuscenes.org/nuimages)

#### Libraries
Libraries used to apply the watermarks.

* [Blind watermark](https://pypi.org/project/blind-watermark/)
* [Invisible watermark](https://pypi.org/project/invisible-watermark/)

`VideoDigitalWatermarking` was not used but it was an inspiration for the Bit Replacement algorithm, the only time-domain watermarking algorithm used in this project.

* [Video Digital Watermarking](https://github.com/piraaa/VideoDigitalWatermarking)

<!-- GETTING STARTED -->
## Getting Started

All the necessary packages are listed in `requirements.txt`.\
Use the following command to install them:
```sh
pip install -r requirements.txt
```

<!-- USAGE EXAMPLES -->
## Usage

All the code is stored in the `src/` folder.\
The simulation flow can be tuned through the environment variables in `src/header.py` and the most important variables are:

* `IMGS_PATH`: root folder of the images used in the simulations; 
* `WM_SIZE_COMP`: 'True' to compute the maximum watermark size in bytes, 'False' otherwise;
* `WM_BSIZE`: maximum watermark size in bytes;
* `WM_PATH`: root folder of the watermarks used in the simulations;
* `WM_TYPES`: allowed watermarks types;
* `WM_TYPE`: currently used watermark type;
* `WM_STR_FILE`: string watermarks file (one per line); 
* `BIT_REPLACEMENT`, `BLIND_WM` and `INV_WM`: 'True' to consider that algorithm in the simulation, 'False' otherwise;
* `DEBUG_BR`, `DEBUG_BW` and `DEBUG_IW`: 'True' to debug a specific algorithm (that algorithm has to be active);
* `SIM_RES_PATH`: root folder of the simulation results;
* `DATA_KEYS`: entries of the data structure the simulation results are recorded into; it can be found at the end of `src/main.py`.

After setting up a simulation, it can be started by executing:
```py
cd src
python3 main.py
```
The simulation progress is reported on the terminal and, at the end, the result is recored in a file inside the `simres\` folder. The file name can be found by looking at the `DATA_FILENAME` macro inside `src/header.py`.

At this point the results can be analyzed by executing:
```py
python3 plot.py
```
This will start an interactive menu to select the appropriate file between the ones inside the simulation results folder.

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
