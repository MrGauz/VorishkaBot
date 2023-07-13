using FFMpegCore;
using FFMpegCore.Pipes;
using SkiaSharp;
using SkiaSharp.Skottie;
using TgsConverter;

if (args.Length < 2)
{
    Console.WriteLine("Usage example: converter.exe input.json.or.tgs output.webm.or.mp4");
    return;
}

var bytes = File.ReadAllBytes(args[0]);

if (bytes.IsGZipped())
    bytes = bytes.Decompress();

using var stream = File.Open(args[0], FileMode.Open, FileAccess.Read, FileShare.Read);

double frameRate = 60;

IEnumerable<SKBitmapFrame> CreateFrames()
{
    using var stream = new MemoryStream(bytes);
    if (!Animation.TryCreate(stream, out var a))
        throw new Exception("Failed to create animation");

    frameRate = a.Fps;

    var size = a.Size.ToSizeI();

    var framesCount = (int)Math.Floor(frameRate * a.Duration.TotalSeconds);

    var frames = new List<SKBitmapFrame>(framesCount);


    for (int i = 0; i < framesCount; i++)
    {
        a.SeekFrame(i);

        var bitmap = new SKBitmap(size.Width, size.Height);
        using var canvas = new SKCanvas(bitmap);
        var dstRect = SKRect.Create(size);

        canvas.Clear(SKColors.Transparent);
        a.Render(canvas, dstRect);

        frames.Add(new SKBitmapFrame(bitmap));
    }

    return frames;
}

var frames = CreateFrames();

RawVideoPipeSource videoFramesSource = new(frames) { FrameRate = frameRate };
var success = FFMpegArguments
    .FromPipeInput(videoFramesSource)
    .OutputToFile(args[1], overwrite: true, options => options.WithVideoCodec("vp9").Loop(0))
    .ProcessSynchronously();
