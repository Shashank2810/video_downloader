"""
downloader/selector.py

Selects the best formats from the analyzed video.
"""

from downloader.models import VideoFormat, VideoInfo


class FormatSelector:
    """
    Helper class for selecting video formats.
    """

    def __init__(self, info: VideoInfo):

        self.info = info

    # =====================================================
    # Available Codecs
    # =====================================================

    def codecs(self) -> list[str]:

        codecs = set()

        for fmt in self.info.video_formats:

            codec = fmt.video_codec.lower()

            if codec.startswith("av01"):
                codecs.add("AV1")

            elif codec.startswith("vp9"):
                codecs.add("VP9")

            elif codec.startswith("avc1"):
                codecs.add("H264")

        return sorted(codecs)

    # =====================================================
    # Available Resolutions
    # =====================================================

    def resolutions(self) -> list[int]:

        values = set()

        for fmt in self.info.video_formats:

            if fmt.height:
                values.add(fmt.height)

        return sorted(values, reverse=True)

    # =====================================================
    # Best Overall
    # =====================================================

    def best(self) -> VideoFormat:

        return max(

            self.info.video_formats,

            key=lambda x: (
                x.height or 0,
                x.fps or 0,
                x.tbr or 0,
            ),
        )

    # =====================================================
    # Best Codec
    # =====================================================

    def best_codec(self, codec: str) -> VideoFormat | None:

        codec = codec.upper()

        formats = []

        for fmt in self.info.video_formats:

            vc = fmt.video_codec.lower()

            if codec == "AV1" and vc.startswith("av01"):
                formats.append(fmt)

            elif codec == "VP9" and vc.startswith("vp9"):
                formats.append(fmt)

            elif codec == "H264" and vc.startswith("avc1"):
                formats.append(fmt)

        if not formats:
            return None

        return max(
            formats,
            key=lambda x: (
                x.height or 0,
                x.fps or 0,
                x.tbr or 0,
            ),
        )

    # =====================================================
    # Download Options
    # =====================================================

    def download_options(self) -> list[dict]:
        """
        Returns download options for the UI.
        """

        options = [
            {
                "value": "best",
                "label": "⭐ Best Quality (Recommended)",
            }
        ]

        for fmt in sorted(
            self.info.video_formats,
            key=lambda x: (
                x.height or 0,
                x.fps or 0,
                x.tbr or 0,
            ),
            reverse=True,
        ):

            vc = fmt.video_codec.lower()

            if vc.startswith("av01"):
                codec = "AV1"

            elif vc.startswith("vp9"):
                codec = "VP9"

            elif vc.startswith("avc1"):
                codec = "H.264"

            else:
                codec = fmt.video_codec

            resolution = f"{fmt.height}p" if fmt.height else "Unknown"

            ext = fmt.ext.upper()

            options.append(
                {
                    "value": fmt.format_id,
                    "label": f"{codec} • {resolution} • {ext}",
                }
            )

        return options