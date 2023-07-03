close all
clear all
clc
 
%% FILES LOCATION IN .TIFF 
File = dir('D:\Diffusion_RawData\2022\Experiment_0\Video\frames_3\*.tiff');
 
 
%% READ ALL THE IMAGES SEQUENCE
for i=1:length(File)
    filename=strcat('D:\Diffusion_RawData\2022\Experiment_0\Video\frames_3\',File(i).name);
    I=imread(filename);
    
    %% MORPHOLOGICAL TRANFORMATIONS
    se = strel('disk',5);
    tF = imclose(I,se);
    se2 = strel('disk',10);
    tF2 = imopen(tF,se2);
    
    %% CONVERT THE IMAGE TO GRAYSCALE MORE DESIGNED FOR FLUORESENCE
    Imgray = rgb2gray(I);
    Imgradj = adapthisteq(Imgray); %improve the image contrast
    Imgray2 = imcomplement(Imgradj); %Invert the images to resembLe calcium imaging
    it2 = imbinarize(Imgray,"adaptive",'ForegroundPolarity','bright','Sensitivity',0.3);
    
    %% COVERS THREE DIFFERENT PATWAYS
    path =strcat('D:\Diffusion_RawData\2022\Experiment_0\Video\frames_3\save_1\',File(i).name);
    %path =strcat('C:\Users\curro\Documents\UCSC_Academics\5 Qtr Courses\237 Imaging processing\Assigment\Scripts\FRAMES\frames\save\Transform\',File(i).name);
    %path =strcat('C:\Users\curro\Documents\UCSC_Academics\5 Qtr Courses\237 Imaging processing\Assigment\Scripts\FRAMES\frames\save\Procesed\',File(i).name);
    
    %% WROTE THE IMAGES IN THE FOLDER
    %imwrite(Imgray2,path);
    imwrite(it2,path);
    
end
