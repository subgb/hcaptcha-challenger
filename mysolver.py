import typing
import time
import sys
sys.path.append("src")
from loguru import logger
from apis.scaffold import install
import hcaptcha_challenger as solver
from hcaptcha_challenger.exceptions import ChallengePassed


def _motion(sample_site: str, ctx, challenger: solver.HolyChallenger) -> typing.Optional[str]:
    resp = None
    ctx.get(sample_site)
    if challenger.utils.face_the_checkbox(ctx):
        challenger.anti_checkbox(ctx)
        resp = challenger.anti_hcaptcha(ctx)
    return resp

@logger.catch()
def run_solver(
        sample_site,
        proxy = None,
        onnx_prefix = "yolov6n", # yolov5n6 yolov5s6 yolov5m6 yolov6n yolov6t yolov6s
        lang = "en",
        silence = False,
        screenshot = False,
        repeat = 5,
    ):
    challenger = solver.new_challenger(screenshot=screenshot, debug=True, lang=lang, onnx_prefix=onnx_prefix)
    ctx = solver.get_challenge_ctx(silence=silence, lang=lang, proxy=proxy)
    for i in range(repeat):
        start = time.time()
        try:
            if (resp := _motion(sample_site, ctx=ctx, challenger=challenger)) is None:
                logger.warning("UnknownMistake")
            elif resp == challenger.CHALLENGE_SUCCESS:
                challenger.log(f"End of demo - total: {round(time.time() - start, 2)}s")
                logger.success(f"PASS[{i + 1}|{repeat}]".center(28, "="))

                answer = challenger.utils.get_hcaptcha_response(ctx)
                print("[ANSWER]", answer)
                sys.stdout.flush()
                return
            elif resp == challenger.CHALLENGE_RETRY:
                ctx.refresh()
                logger.error(f"RETRY[{i + 1}|{repeat}]".center(28, "="))
        except ChallengePassed:
            ctx.refresh()
            logger.success(f"PASS[{i + 1}|{repeat}]".center(28, "="))


install.do()
if __name__ == "__main__":
    uuid = sys.argv[1] if len(sys.argv)>1 else "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"
    proxy = sys.argv[2] if len(sys.argv)>2 else None
    show = len(sys.argv)>3
    run_solver(
        sample_site = f"https://accounts.hcaptcha.com/demo?sitekey={uuid}",
        proxy = proxy,
        silence = not show,
    )

