from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from manim import config

from binary_scenes import FixedToFloatingScene, rename_rendered_video


class FixedToFloatingVideo(FixedToFloatingScene):
    pass


def main() -> None:
    parser = ArgumentParser(description="Render a fixed-to-floating-point example video")
    parser.add_argument("--denary", type=float, default=11.5625)
    parser.add_argument("--integer-bits", type=int, default=4)
    parser.add_argument("--fraction-bits", type=int, default=4)
    parser.add_argument("--mantissa-bits", type=int, default=8)
    parser.add_argument("--exponent", type=int)
    parser.add_argument("--exponent-bits", type=int, default=4)
    parser.add_argument(
        "--detailed",
        action=BooleanOptionalAction,
        default=False,
        help="Show right-to-left denary to fixed-binary breakdown animation",
    )
    parser.add_argument(
        "--headers",
        action=BooleanOptionalAction,
        default=False,
        help="Show denary bit-weight headers above fixed-binary columns",
    )
    args = parser.parse_args()

    config.media_dir = str(Path.cwd() / "media")
    scene = FixedToFloatingVideo(
        denary_value=args.denary,
        integer_bits=args.integer_bits,
        fraction_bits=args.fraction_bits,
        mantissa_bits=args.mantissa_bits,
        exponent=args.exponent,
        exponent_bits=args.exponent_bits,
        detailed_conversion=args.detailed,
        show_headers=args.headers,
    )
    scene.render()
    denary_tag = f"{args.denary:g}".replace("-", "neg").replace(".", "p")
    options = []
    if args.detailed:
        options.append("detailed")
    if args.headers:
        options.append("headers")
    option_suffix = "_" + "_".join(options) if options else ""
    exp_tag = args.exponent if args.exponent is not None else "auto"
    final_name = (
        f"fixed_to_floating_d{denary_tag}_i{args.integer_bits}_f{args.fraction_bits}_m{args.mantissa_bits}"
        f"_exp{exp_tag}_bits{args.exponent_bits}{option_suffix}"
    )
    renamed = rename_rendered_video(scene.__class__.__name__, final_name)
    print(f"Saved {renamed}")


if __name__ == "__main__":
    main()
