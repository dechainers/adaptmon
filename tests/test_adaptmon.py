# Copyright 2022 DeChainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest

from dechainy.controller import Controller
from dechainy.plugins import HookSetting, Probe
from dechainy.exceptions import MetricUnspecifiedException

controller = Controller()

code = """
BPF_TABLE("array", int, int, ATTEMPT, 1)__attributes__(EXPORT);
BPF_TABLE("array", int, int, NO_ATTEMPT, 1);
static __always_inline int handler(struct CTXTYPE *ctx, struct pkt_metadata *md) {
    return PASS;
}

"""

@unittest.skipIf(os.getuid(), reason='Root for BCC')
class TestAdaptmon(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        controller.delete_probe(plugin_name='adaptmon')
        controller.delete_plugin('adaptmon')

    def test1_add_plugin(self):
        controller.create_plugin(os.path.join(os.path.dirname(
            __file__), os.pardir, "adaptmon"), update=True)

    def test2_create_probe(self):
        controller.create_probe('adaptmon', 'attempt', interface='lo', ingress=HookSetting(required=True, code=code))

    def test3_get_metric(self):
        p: Probe = controller.get_probe('adaptmon', 'attempt')
        p.retrieve_metric("ingress", "ATTEMPT")
        
    def test4_get_metric_no_export(self):
        p: Probe = controller.get_probe('adaptmon', 'attempt')
        with self.assertRaises(MetricUnspecifiedException):
            p.retrieve_metric("ingress", "NO_ATTEMPT")

if __name__ == '__main__':
    unittest.main()