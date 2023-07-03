% import the video file
obj = VideoReader('ShortVideo.mp4');
vid = read(obj);

% read the total number of frames
frames = obj.NumFrames;

% file format of the frames to be saved in
ST ='.tiff';

% reading and writing the frames
for x = 1: 20 : frames
	% converting integer to string
	Sx = num2str(x);

	% concatenating 2 strings
	Strc = strcat(Sx, ST);
	Vid = vid(:, :, :, x);
	cd frames

	% exporting the frames
	imwrite(Vid, Strc);
	cd ..
end
