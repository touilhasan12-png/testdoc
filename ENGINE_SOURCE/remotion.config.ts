import {Config} from '@remotion/cli/config';
// GitHub hosted Linux runners generally have no GPU. Swangle is software WebGL.
Config.setChromiumOpenGlRenderer('swangle');
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
