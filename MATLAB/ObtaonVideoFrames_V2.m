FishVid = VideoReader('A015 - 20210407_162652.wmv')
VidInfo=get(FishVid);
    numberOfFrames = FishVid.NumberOfFrames;
    vidHeight = FishVid.Height;
    vidWidth = FishVid.Width;

   i= 1;
   while i <= numberOfFrames
   currentFrame = read(VidInfo,numberOfFrames); 
   combinedString=strcat(int2str(i-1),'.jpg');
   imwrite(currentFrame,combinedString);
   i=i+700;
   end