import fontTool
import DDSTool
import jmbUtils
from jmbDefine import gDat

from copy import copy, deepcopy
import unittest
from unittest import TestCase

jmk00010101 : list[list[str]] = [
    [
        "そこが巣だ",
        "このアパートが？",
    ],
    [
        "連中の群れだ",
        "調べでは、14匹が棲みついている",
    ],
    [
        "全部、殺っていいのか？",
    ],
    [
        "1匹は、生け捕りにしてくれ",
        "ココの親玉が居るはずだ",
    ],
    [
        "情報は？",
    ],
    [
        "会えばわかるさ",
        "“笑う顔”とは決定的に違う",
    ],
    [
        "了解した",
    ],
    [
        "神に笑いを…",
    ],
    [
        "悪魔に慈悲を…"
    ],
]

class JMBBaseTask(TestCase):
    jmb = gDat()
    context = {}

    @classmethod
    def set_context(cls, jmb:gDat, shared_context: dict):
        cls.jmb = jmb
        cls.context = shared_context

    def runTest(self):
        self.execute()

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

class JMBTestLoader(unittest.TestLoader):
    def __init__(self, jmb:gDat=None, shared_context: dict = None):
        super().__init__()
        self.jmb = jmb
        self.shared_context = shared_context or {}

    def loadTestsFromTestCase(self, testCaseClass):
        if issubclass(testCaseClass, JMBBaseTask):
            testCaseClass.set_context(self.jmb, self.shared_context)
        return super().loadTestsFromTestCase(testCaseClass)

def basicTask(func):
    class Task(JMBBaseTask):
        def execute(self):
            return func(self)
    Task.__name__ = func.__name__
    Task.__doc__ = func.__doc__
    return Task

@basicTask
def TaskValidation(self:JMBBaseTask):
    """
    测试读取后，根据其生成的jmb是否能跟原文件一样
    """
    original_path = self.context.get('original_path')
    print("\n==== Validation ====")
    result = self.jmb.no_diff_with(original_path)
    print(f"Validation Result: {result}")
    if not result:
        self.fail("Validation failed!")

@basicTask
def TaskRegenerate_SMALLER(self:JMBBaseTask):
    """
    测试读取后，重新生成自己的DDS（但是更小）和对应的sentence，能否成功
    """
    unique_chars = self.context['unique_chars']
    print("\n==== Regenerating Smaller DDS ====")

    DDSTool.gen("gen.dds", unique_chars, fixed_max_width=False) # NOTE: SMALLER
    self.jmb.reimport_tex("gen.dds")

@basicTask
def TaskRegenerate_BIGGER(self:JMBBaseTask):
    """
    测试读取后，重新生成自己的DDS（但是更大），能否成功
    """
    unique_chars = self.context['unique_chars']
    print("\n==== Regenerating Bigger DDS ====")

    DDSTool.gen("gen.dds", unique_chars, fixed_max_width=True) # NOTE: BIGGER
    self.jmb.reimport_tex("gen.dds")

@basicTask
def TaskGeneratePreview(self:JMBBaseTask):
    preview_dir = self.context.get('preview_dir', 'jmks')
    ctl2char_lookup = self.context['ctl2char_lookup']
    print("\n==== Generating Previews ====")

    assert(self.jmb.meta.sentence_num == len(self.jmb.sentences))
    for i in range(self.jmb.meta.sentence_num):
        sent = self.jmb.sentences[i]
        print("generating preview for sentence", i)
        for jmk_idx, jmk in enumerate(sent.jimaku_list):
            if not jmk.valid():
                break
            # print("\t char_data:", len(jmk.char_data), jmk.char_data)
            # print("\t rubi_data:", len(jmk.rubi_data), jmk.rubi_data)
            target_path = f"{preview_dir}/sent{i}/{jmk_idx:02d}"
            # jmk.dump(target_path)
            fontTool.save_preview_jimaku(target_path+".png", jmk, ctl2char_lookup)
            # fontTool.save_preview_jimaku(target_path+".png", jmk, ctl2char_lookup, jmb.fParams)

@basicTask
def TaskExtractChars(self:JMBBaseTask):
    extracted_dir = self.context.get('extracted_dir', 'modded_dds_font')
    print("\n==== Extracting Chars From DDS ====")

    DDSTool.extract(extracted_dir, self.jmb.tex.dds, self.jmb.fParams, should_store = True)

@basicTask
def TaskPrintFParams(self:JMBBaseTask):
    print("\n==== Printing FParams ====")
    for param in self.jmb.fParams:
        print(param)

@basicTask
def TaskPrintDDSInfo(self:JMBBaseTask):
    print("\n==== Printing DDS Info ====")
    print("tex_offset =", self.jmb.meta.tex_offset)
    print("header =", self.jmb.tex.header)
    DDSTool.print_info(self.jmb.tex.dds)
    print("jmb after_tex_pos =", self.jmb.meta.s_motion_offset)

@basicTask
def TaskSave(self:JMBBaseTask):
    """
    单纯的保存为文件
    """
    output_path = self.context.get('output_path', 'testmod.jmb')
    print("\n==== Saving Modified File ====")

    self.jmb.write_to_file(output_path)
    print(f"File saved to: {output_path}")

class TaskTranslation(JMBBaseTask):
    """
    修改一部分文字
    """
    def execute(self):
        print("\n==== Modifying Translation ====")
        translation = deepcopy(jmk00010101)
        translation[0][0] = "這里就是老巣了"
        translation[0][1] = "就這鳥地方？"
        translation[1][0] = "都扎堆在這里"
        translation[1][1] = "調査結果 総共有14匹"
        translation[2][0] = "全都可以殺了吧？"
        translation[3][0] = "至少 留着1個活口吧"
        translation[3][1] = "先問出他們老闆在哪児"
        translation[4][0] = "有情報麽？"
        translation[5][0] = "親眼看看你就懂了"
        translation[5][1] = "和“笑顔”有決定性的不同"
        translation[6][0] = "了解"
        translation[7][0] = "愿上帝微笑…"
        translation[8][0] = "願悪魔慈悲…"

        jmbUtils.print_jmt_differences(jmk00010101, translation)

        text_flatten = ''.join(t for s in translation for t in s)
        ctl2char_lookup, char2ctl_lookup, unique_chars = fontTool.register(text_flatten)
        self.context.update({
            'text': translation,
            'text_flatten': text_flatten,
            'ctl2char_lookup': ctl2char_lookup,
            'char2ctl_lookup': char2ctl_lookup,
            'unique_chars': unique_chars
        })

        self.jmb.fParams = fontTool.genFParams(unique_chars)
        self.jmb.update_sentence_ctl(translation, char2ctl_lookup, validation_mode=False)



def run_tasks(input_path:str, tasks:list[type], **task_args):
    task_args['original_path'] = input_path
    with open(input_path, 'rb') as fp:
        jmb = gDat(fp)

    shared_context = {}

    # 提前处理文本数据并存入context
    text = deepcopy(jmk00010101)
    text_flatten = ''.join(t for s in text for t in s)
    ctl2char_lookup, char2ctl_lookup, unique_chars = fontTool.register(text_flatten)

    shared_context.update({
        'text': text,
        'text_flatten': text_flatten,
        'ctl2char_lookup': ctl2char_lookup,
        'char2ctl_lookup': char2ctl_lookup,
        'unique_chars': unique_chars,
        **task_args  # 包含所有传入参数
    })

    loader = JMBTestLoader(jmb=jmb, shared_context = shared_context)

    suite = unittest.TestSuite()
    for task in tasks:
        suite.addTest(loader.loadTestsFromTestCase(task))

    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite)

if __name__ == '__main__':
    files = [
        "D:/SteamLibrary/steamapps/common/killer7/Extracted/CharaGeki/00010101/00010101_BACKUP/00010101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/Extracted/CharaGeki/00020103/00020103/00020103J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/Extracted/CharaGeki/00020707/00020707/00020707J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/Extracted/CharaGeki/00020709/00020709/00020709J.jmb",
    ]

    tasks = [
        TaskValidation,
        # TaskPrintFParams,
        TaskPrintDDSInfo,
        TaskTranslation,
        # TaskGeneratePreview,
        TaskRegenerate_SMALLER,
        TaskSave,
    ]

    for file in files:
        run_tasks(
            file,
            tasks,

            output_path="testmod.jmb",
            preview_dir="jmks"
        )