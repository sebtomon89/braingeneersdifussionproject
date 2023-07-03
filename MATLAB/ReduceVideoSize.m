a = VideoReader('A002 - 20220715_144349.wmv');
beginFrame = 100 * a.FrameRate;
endFrame = 5000 * a.FrameRate;
vidObj = VideoWriter('ShortVideo', 'MPEG-4');
%vidObj.VideoCompressionMethod;
vidObj.Quality = 50;
open(vidObj);
for img = beginFrame:20:endFrame
    b = read(a, img);
    writeVideo(vidObj,b)
end
close(vidObj);