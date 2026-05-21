from argparse import ArgumentParser
from pathlib import Path

from manim import config

from binary_scenes import TwosComplementScene, rename_rendered_video


class TwosComplementVideo(TwosComplementScene):
    pass


def main() -> None:
    parser = ArgumentParser(description="Render a two's complement example video")
    parser.add_argument("--value", type=int, default=43)
    parser.add_argument("--bits", type=int, default=8)
    args = parser.parse_args()

    config.media_dir = str(Path.cwd() / "media")
    scene = TwosComplementVideo(value=args.value, bits=args.bits)
    scene.render()
    final_name = f"twos_complement_neg{args.value}_bits{args.bits}"
    renamed = rename_rendered_video(scene.__class__.__name__, final_name)
    print(f"Saved {renamed}")


if __name__ == "__main__":
    main()
