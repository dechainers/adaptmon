import os

from dechainy.exceptions import NoCodeProbeException
from dechainy.plugins import HookSetting, Probe


class Adaptmon(Probe):
    def __post_init__(self):
        written = []
        for ttype in ["ingress", "egress"]:
            hook: HookSetting = getattr(self, ttype)
            if not hook.required:
                continue
            if not hook.code:
                raise NoCodeProbeException(
                    "No code for hook {} for the probe {}".format(ttype, self.name))
            written.append(os.path.join(
                os.path.dirname(__file__), "{}.c".format(ttype)))
            with open(written[-1], "w") as fp:
                fp.write(hook.code)
        super().__post_init__(path=__file__)
        [os.remove(x) for x in written]
