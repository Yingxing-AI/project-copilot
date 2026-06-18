import unittest

from project_copilot.intent import Intent, classify_intent, classify_intent_name


class IntentClassifierTest(unittest.TestCase):
    def test_classifies_project_check_variants(self) -> None:
        self.assertEqual(classify_intent("帮我看看项目怎么样"), Intent.CHECK_PROJECT)
        self.assertEqual(classify_intent("当前项目状态如何"), Intent.CHECK_PROJECT)

    def test_classifies_core_workflows(self) -> None:
        self.assertEqual(classify_intent("这是一个 AI 招聘系统，请初始化项目"), Intent.INIT_PROJECT)
        self.assertEqual(classify_intent("接管这个已有项目"), Intent.ADOPT_PROJECT)
        self.assertEqual(classify_intent("继续开发项目"), Intent.CONTINUE_DEV)
        self.assertEqual(classify_intent("今天结束工作"), Intent.END_WORK)
        self.assertEqual(classify_intent("检查 OSS 准备度"), Intent.CHECK_OSS)
        self.assertEqual(classify_intent("准备开源"), Intent.PREPARE_OSS)
        self.assertEqual(classify_intent("私有同步到GitHub"), Intent.GITHUB_SYNC)
        self.assertEqual(classify_intent("发布版本 v0.3.0-alpha.2"), Intent.RELEASE_PROJECT)
        self.assertEqual(classify_intent("发布 v0.3.0-alpha.2"), Intent.RELEASE_PROJECT)
        self.assertEqual(classify_intent("同步项目状态"), Intent.SYNC_PROJECT_STATE)
        self.assertEqual(classify_intent("项目复盘"), Intent.REVIEW_PROJECT)
        self.assertEqual(classify_intent("项目时间轴"), Intent.TIMELINE_PROJECT)
        self.assertEqual(classify_intent("项目偏航检查 新增商城模块"), Intent.DRIFT_CHECK)
        self.assertEqual(classify_intent("记录决策 MVP 先做简历导入"), Intent.RECORD_DECISION)
        self.assertEqual(classify_intent("查看路线图"), Intent.SHOW_ROADMAP)
        self.assertEqual(classify_intent("刷新验证报告"), Intent.REFRESH_VALIDATION_REPORT)
        self.assertEqual(classify_intent("导出验证快照"), Intent.EXPORT_VALIDATION_SNAPSHOT)

    def test_outputs_standard_intent_name(self) -> None:
        self.assertEqual(classify_intent_name("继续开发项目"), "continue_development")
        self.assertEqual(classify_intent_name("今天结束工作"), "close_day")
        self.assertEqual(classify_intent_name("检查 OSS 准备度"), "oss_check")
        self.assertEqual(classify_intent_name("准备开源"), "prepare_oss")
        self.assertEqual(classify_intent_name("开源到GitHub"), "github_sync")
        self.assertEqual(classify_intent_name("创建 GitHub Release v0.3.0-alpha.2"), "release_project")
        self.assertEqual(classify_intent_name("同步文档"), "sync_project_state")
        self.assertEqual(classify_intent_name("项目复盘"), "review_project")
        self.assertEqual(classify_intent_name("刷新验证报告"), "refresh_validation_report")
        self.assertEqual(classify_intent_name("导出验证快照"), "export_validation_snapshot")

    def test_unknown_intent_is_explicit(self) -> None:
        self.assertEqual(classify_intent("随便说点无法识别的话"), Intent.UNKNOWN)
        self.assertEqual(classify_intent_name("随便说点无法识别的话"), "unknown")
