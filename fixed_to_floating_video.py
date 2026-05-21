from argparse import ArgumentParser
from pathlib import Path

from manim import config

from binary_scenes import FixedToFloatingScene, rename_rendered_video


class FixedToFloatingVideo(FixedToFloatingScene):
    pass


def main() -> None:
    parser = ArgumentParser(description="Render a fixed-to-floating-point example video")
    parser.add_argument("--fixed-value", default="1101.0000")
    parser.add_argument("--exponent", type=int, default=4)
    parser.add_argument("--exponent-bits", type=int, default=4)
    args = parser.parse_args()

    config.media_dir = str(Path.cwd() / "media")
    scene = FixedToFloatingVideo(
        fixed_value=args.fixed_value,
        exponent=args.exponent,
        exponent_bits=args.exponent_bits,
    )
    scene.render()
    fixed_tag = args.fixed_value.replace(".", "p")
    final_name = f"fixed_to_floating_{fixed_tag}_exp{args.exponent}_bits{args.exponent_bits}"
    renamed = rename_rendered_video(scene.__class__.__name__, final_name)
    print(f"Saved {renamed}")


if __name__ == "__main__":
    main()
