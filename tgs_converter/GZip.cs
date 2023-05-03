using System.IO.Compression;

namespace TgsConverter;

public static class GZip
{
    public static bool IsGZipped(this byte[]? bytes)
    {
        if (bytes is null or { Length: < 2 })
            return false;

        return bytes[0] == 0x1f && bytes[1] == 0x8b;
    }

    public static byte[] Decompress(this byte[] gZippedBytes)
    {
        using var compressedStream = new MemoryStream(gZippedBytes);
        using var gzipStream = new GZipStream(compressedStream, CompressionMode.Decompress);
        using var decompressedStream = new MemoryStream();

        const int bufferSize = 8192;
        Span<byte> buffer = stackalloc byte[bufferSize];
        int bytesRead;

        while ((bytesRead = gzipStream.Read(buffer)) > 0)
        {
            decompressedStream.Write(buffer[..bytesRead]);
        }

        return decompressedStream.ToArray();
    }
}
