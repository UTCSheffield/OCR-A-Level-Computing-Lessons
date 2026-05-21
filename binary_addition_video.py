from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from manim import config

from binary_scenes import BinaryAdditionScene, rename_rendered_video


class BinaryAdditionVideo(BinaryAdditionScene):
    pass


def main() -> None:
    parser = ArgumentParser(description="Render a binary addition example video")
    parser.add_argument("--a", type=int, default=165)
    parser.add_argument("--b", type=int, default=143)
    parser.add_argument("--bits", type=int, default=8)
    parser.add_argument(
        "--detailed",
        action=BooleanOptionalAction,
        default=False,
        help="Show right-to-left denary to binary breakdown animation",
    )
    parser.add_argument(
        "--headers",
        action=BooleanOptionalAction,
        default=False,
        help="Show denary bit-weight column headers above binary columns",
    )
    args = parser.parse_args()

    config.media_dir = str(Path.cwd() / "media")
    scene = BinaryAdditionVideo(
        a=args.a,
        b=args.b,
        bits=args.bits,
        detailed_conversion=args.detailed,
        show_denary_headers=args.headers,
    )
    scene.render()
    options = []
    if args.detailed:
        options.append("detailed")
    if args.headers:
        options.append("headers")
    option_suffix = "_" + "_".join(options) if options else ""
    final_name = f"binary_addition_a{args.a}_b{args.b}_bits{args.bits}{option_suffix}"
    renamed = rename_rendered_video(scene.__class__.__name__, final_name)
    print(f"Saved {renamed}")


if __name__ == "__main__":
    main()
