# _*_ coding:utf-8_*_
import os


def _get_pdf_page_count(file_path: str) -> int:
    """获取PDF页数"""
    try:
        try:
            from PyPDF2 import PdfReader
            with open(file_path, 'rb') as f:
                return len(PdfReader(f).pages)
        except ImportError:
            pass

        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except ImportError:
            pass

        try:
            import fitz
            doc = fitz.open(file_path)
            page_count = doc.page_count
            doc.close()
            return page_count
        except ImportError:
            pass

        return 0
    except Exception as e:
        print(f"warning: 获取PDF页数失败: {e}")
        return 0

def extract_with_pymupdf4llm(temp_file_path: str, filename: str) -> tuple:
    """使用 PyMuPDF4LLM 提取PDF文本和页数"""
    try:
        from langchain_pymupdf4llm import PyMuPDF4LLMLoader
        from langchain_community.document_loaders.parsers import LLMImageBlobParser

        print(f"使用 PyMuPDF4LLM 解析PDF: {filename}")

        # 检查是否启用多模态处理
        enable_multimodal = os.getenv("ENABLE_PDF_MULTIMODAL", "true").lower() == "true"

        if enable_multimodal:
            try:
                _PROMPT_IMAGES_TO_DESCRIPTION: str = (
                    "您是一名负责为图像检索任务生成摘要的助手。"
                    "1. 这些摘要将被嵌入并用于检索原始图像。"
                    "请提供简洁的图像摘要，确保其高度优化以利于检索\n"
                    "2. 提取图像中的所有文本内容。"
                    "不得遗漏页面上的任何信息。\n"
                    "3. 不要凭空捏造不存在的信息\n"
                    "请使用Markdown格式直接输出答案，"
                    "无需解释性文字，且开头不要使用Markdown分隔符```。"
                )
                print("使用多模型模型处理PDF")
                from app.core.llm import vision_model
                image_parser = LLMImageBlobParser(model=vision_model(),
                                                  prompt=_PROMPT_IMAGES_TO_DESCRIPTION)

                loader = PyMuPDF4LLMLoader(
                    temp_file_path,
                    mode="page",
                    extract_images=True,
                    images_parser=image_parser,
                    table_strategy="lines"
                )
            except Exception as e:
                print(f"warning: 多模态处理失败: {e}，使用标准模式")
                print("不使用多模型模型处理PDF")
                loader = PyMuPDF4LLMLoader(temp_file_path, mode="single", table_strategy="lines")
        else:
            print("不使用多模型模型处理PDF")
            loader = PyMuPDF4LLMLoader(temp_file_path, mode="page", table_strategy="lines")

        documents = loader.load()
        print(f"PyMuPDF4LLM 解析PDF: {documents}")
        page_count = _get_pdf_page_count(temp_file_path)

        if documents:
            text_content = documents[0].page_content
            print(f"PyMuPDF4LLM 解析成功，内容长度: {len(text_content)} 字符， 页数: {page_count}")
            return text_content, page_count
        else:
            return "PDF文件解析后内容为空", page_count
    except ImportError as e:
        raise ImportError(str(e))

temp_file_path=r"./旅行日记.pdf"
filename="旅行日记.pdf"
extract_with_pymupdf4llm(temp_file_path, filename)

"""
PyMuPDF4LLM 解析PDF(singer mode): 
[
    Document(
        metadata={'producer': 'Skia/PDF m86', 
                  'creator': 
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 
                  'creationdate': '2020-11-23T02:03:36+00:00', 
                  'source': 'E:\\学习资料.pdf', 
                  'file_path': 'E:\\学习资料.pdf', 
                  'total_pages': 5, 
                  'format': 'PDF 1.4', 
                  'title': '', 
                  'author': '', 
                  'subject': '', 
                  'keywords': '', 
                  'moddate': '2020-11-23T02:03:36+00:00', 
                  'trapped': '', 
                  'modDate': "D:20201123020336+00'00'", 
                  'creationDate': "D:20201123020336+00'00'"
                  }, 
        page_content='2020/11/23 【全员学习】生产环境操作规范考试@20201123\n\n\n剩余时间: 00:25:32\n\n# **【全员学习】生产环境操作规范考试@20201123**\n\n\n总分:100.0分 考试时长:40分钟 总题量:20题\n\n\n考试说明: 1、考试时间40分钟 2、及格分数线为90分 3、祝各位考试顺利\n\n\n**单选题**\n\n\n1. 为了减少发布过程的出错率，公司要求发布人员根据上线程序清单，通过（）将程序部署至生产环境(本题\n分数：5.0分)( 答案不确定)\n\n\n\n![### Summary:  \nA list of four Chinese radio button options: 手动 (Manual), 拷贝 (Copy), 批量拷贝 (Batch Copy), 云管理平台 (Cloud Management Platform), with 云管理平台 selected (blue filled circle).  \n\n\n### Extracted Text:  \n手动  \n拷贝  \n批量拷贝  \n云管理平台](#)\n\n\n\n2. 生产环境需求测试过程中，出现未测试通过的需求，下列做法正确的是（）(本题分数：5.0分)( 答案不确\n定)\n\n\n\n![### Summary  \nMultiple - choice (radio buttons) list with 4 options for actions after problem identification; the selected option is "回退该需求代码并进行回退测试" (Roll back the requirement code and perform rollback testing). Other options: re - send to release personnel, self - login to host, private communication with bureau personnel.  \n\n### Extracted Text  \n- 定位到问题后，对生产影响不大，重新发给发布人员进行上线  \n- 定位到问题后，对生产影响不大，自己登录主机上线  \n- 私自和局方人员沟通后上线  \n- 回退该需求代码并进行回退测试](#)\n\n\n\n\n\n3. 在生产环境对上线内容进行测试，如果发现的问题影响了生产环境，此申请单内容（）(本题分数：5.0分)(\n\n答案不确定)\n\n\n\n![### Summary  \nA set of four radio buttons with Chinese text; the first option "回退" is selected, while the others ("重新测试", "修改测试用例", "以上都正确") are unselected.  \n\n\n### Extracted Text  \n回退  \n重新测试  \n修改测试用例  \n以上都正确](#)\n\n\n\n\n\n4. 对生产上线后问题复盘，说法错误的是（）(本题分数：5.0分)( 答案不确定)\n\n\n分析上线过程中遇到的问题\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 1/5\n\n\n\n-----\n\n|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n|||分析上线测试过程中的问题<br>剩余时间:00:25:32|||\n|||分析具体原因并制定改进计划|分析具体原因并制定改进计划|分析具体原因并制定改进计划|\n|||问题复盘针对组长就可以了，开发人员不用参加|问题复盘针对组长就可以了，开发人员不用参加|问题复盘针对组长就可以了，开发人员不用参加|\n\n\n5. 生产环境上线过程中，局方要求修改与本次上线无关的代码文件你会怎么做（）(本题分数：5.0分)( 答案\n不确定)\n\n\n6. 小丁是一名运维人员，局方找到他，要求他删除一条生产数据库中的错误数据，小丁的哪个做法是错误的\n（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary:  \nA set of four Chinese radio - button options (for handling a modification), with the third option ("上报项目经理和技术负责人进行评估") selected.  \n\n\n### Extracted Text:  \n1. 改动较小，没什么影响，直接修改  \n2. 和局方人员关系不错直接修改  \n3. 上报项目经理和技术负责人进行评估  \n4. 已上都不正确](#)\n\n![### 图像总结  \n包含三个单选选项的列表，**第一个选项（“比较简单，直接按照局方要求写sql语句删除”）被蓝色圆点选中**，其余两个选项为：“让局方人员直接找项目经理或者组长”、“写好sql语句并找组长进行审核，并按照流程申请权限、账号后进行操作”。  \n\n\n### 提取的文本  \n1. 比较简单，直接按照局方要求写sql语句删除  \n2. 让局方人员直接找项目经理或者组长  \n3. 写好sql语句并找组长进行审核，并按照流程申请权限、账号后进行操作](#)\n\n\n\n7. 生产上线测试过程中发现上线版本不正确，下列做法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary:  \nA list of four radio - button options for handling code deployment. The option “通知发布人员回退本次上线代码” (Notify the release personnel to roll back the code of this release) is selected. The other options are “重新发一版本给发布人员上线” (Resend a version for the release personnel to release), “自己登录主机上线代码” (Log in to the host to release the code by oneself), and “影响不大，暂时不管” (The impact is not significant, leave it for now).  \n\n\n### Extracted Text:  \n- 重新发一版本给发布人员上线  \n- 自己登录主机上线代码  \n- 通知发布人员回退本次上线代码  \n- 影响不大，暂时不管](#)\n\n\n\n\n\n8. 针对生产环境的操作，下面描述正确的是(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Image Summary  \nA multiple-choice question (radio buttons) about operational permissions in a production environment. The **selected option** (blue dot) states: *"运维人员需要提交申请，审核通过后方可操作生产环境"* (Operations personnel must submit an application; approval is required to operate the production environment). Two unselected options address unauthorized/unsupervised operations.  \n\n\n### Extracted Text  \n1. 未经局方许可，项目经理可以直接赋权给运维人员进行操作  \n2. 不用申请，运维组长可以直接在生产环境上进行操作  \n3. 运维人员需要提交申请，审核通过后方可操作生产环境](#)\n\n\n\n\n\n9. 关于上线评审会的描述，不正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n上线评审会只对上线需求范围做审核\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 2/5\n\n\n\n-----\n\n|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n|||会中对上线需求的各种文档和存在的风险进行评审<br>剩余时间:00:25:32|||\n|||会中对上线需求范围进行评审|会中对上线需求范围进行评审|会中对上线需求范围进行评审|\n|||会中对上线所需资源进行评审|会中对上线所需资源进行评审|会中对上线所需资源进行评审|\n\n\n10. 关于上线前代码是否需要安全扫描说法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary:  \nA multiple - choice question (in Chinese) about code scanning for different deployment types (emergency, normal, non - emergency deployment of code). The option “以上都不正确 (None of the above)” is selected (indicated by a blue radio button).  \n\n\n### Extracted Text:  \n紧急上线的代码不需要扫描  \n正常上线的代码不需要扫描代码  \n非紧急上线的代码需要代码扫描，紧急上线的代码不需要扫描  \n以上都不正确](#)\n\n\n\n11. 账号申请成功之后可登陆生产环境，以下对生产环境操作描述正确的是（）(本题分数：5.0分)( 答案不\n确定)\n\n\n\n![### Summary  \nImage shows a multiple - choice (radio - button) interface with 4 options about production - host operation rules (host confirmation, command - list approval, crontab task restrictions). The last option “以上都正确” (All above are correct) is selected (blue radio button).  \n\n\n### Extracted Text  \n1. 在生产主机上操作，需用hostname - i 确认是否是该生产主机。pwd确认是否是所在的目录  \n2. 根据项目，需求，运维实际操作需求，提供操作命令列表，方式。需要对应接口人审核后方可进行操作  \n3. 未经对应负责人同意，禁止停启crontab任务或进程  \n4. 以上都正确](#)\n\n\n\n\n\n12. 关于生产环境扫描出来的漏洞解决方法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nImage displays a radio - button (multiple - choice) list with four options related to system vulnerability handling. The second option ("安全负责人和技术负责人制定漏洞方案，给出上线时间") is selected.  \n\n\n### Extracted Text  \n1. 不影响生产业务办理，暂时不用修改  \n2. 安全负责人和技术负责人制定漏洞方案，给出上线时间  \n3. 没有人通过漏洞攻击系统，暂时不用管  \n4. 以上说法都不正确](#)\n\n\n\n\n\n13. 生产上线过程中对某些文件没有操作权限的情况，以下做法正确的是（）(本题分数：5.0分)( 答案不确\n定)\n\n\n\n![### 图像总结  \n单选选项列表含4项，围绕用户权限操作/申请流程，最后一项（“上报组长和项目经理，等待权限申请后操作上线”）被选中。选项内容：  \n- 当前用户切换到root用户执行  \n- 当前用户切换到root用户，给当前用户赋权  \n- 使用本机其他用户，尝试进行权限赋权等操作  \n- 上报组长和项目经理，等待权限申请后操作上线  \n\n\n### 提取文本  \n- 当前用户切换到root用户执行  \n- 当前用户切换到root用户，给当前用户赋权  \n- 使用本机其他用户，尝试进行权限赋权等操作  \n- 上报组长和项目经理，等待权限申请后操作上线](#)\n\n\n\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 3/5\n\n\n\n-----\n\n账号、申请人、同意人、开始时间、结束时间、事由\n\n|Col1|020/11/23 【全员学习】生产环境操作规范考试@20201123|Col3|\n|---|---|---|\n||14.小张入职不足一年，生产环境当晚需要重启服务，他的做法错误的是（）(本题分数：5.0分)(<br>答案不确<br>定)<br>剩余时间:00:25:32||\n||15.关于生产环境操作哪个描述是正确的（）(本题分数：5.0分)(<br>答案不确定)<br>16.生产系统权限申请表包括那些内容（）(本题分数：5.0分)(<br>答案不确定)<br>听从组长安排<br>自己直接重启服务<br>组长和项目经理审批通过，小张重启服务<br>上报组长和项目经理，等待授权后操作<br>未经对应负责人同意禁止运行sqlplus数据库命令<br>未经对应负责人同意禁止修改环境变量<br>未经对应负责人同意禁止在生产环境做程序测试工作<br>以上都正确<br>账号、申请人、同意人<br>账号、申请人、同意人、开始时间、结束时间<br>||\n\n\n\n账号、同意人、开始时间、结束时间、事由、上线时间\n\n\n17. 需求上线当晚，测试过程中发现生产有一个问题，开发人员判断修改生产数据库原有的一个参数配置即\n可。此时发布人员应该（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nInterface with three radio - button options (Chinese). The second option (“上报给组长和项目经理”) is selected. Options: “立即修改” (unselected), “上报给组长和项目经理” (selected), “提供账号给开发人员，让开发人员自己修改” (unselected).  \n\n\n### Extracted Text  \n- 立即修改  \n- 上报给组长和项目经理  \n- 提供账号给开发人员，让开发人员自己修改](#)\n\n\n\n18. 对生产扫描出来的安全漏洞理解正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n简单的漏洞可以直接在生产上修复\n\n\n低级漏洞不修改\n\n\n需要在测试环境上验证通过后才能上线生产环境\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 4/5\n\n\n\n-----\n\n|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n||解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32|解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32|解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32||\n||19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 5/5\n\n\n')]
"""

"""
PyMuPDF4LLM 解析PDF(page mode): 
[
    Document(
        metadata={'producer': 'Skia/PDF m86', 
                  'creator': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 
                  'creationdate': '2020-11-23T02:03:36+00:00', 
                  'source': 'E:\\学习资料.pdf', 
                  'file_path': 'E:\\学习资料.pdf', 
                  'total_pages': 5, 
                  'format': 'PDF 1.4', 
                  'title': '', 'author': '', 
                  'subject': '', 'keywords': '', 
                  'moddate': '2020-11-23T02:03:36+00:00', 
                  'trapped': '', 
                  'modDate': "D:20201123020336+00'00'", 
                  'creationDate': "D:20201123020336+00'00'", 'page': 0
                  }, 
        page_content='2020/11/23 【全员学习】生产环境操作规范考试@20201123\n\n\n剩余时间: 00:25:32\n\n# **【全员学习】生产环境操作规范考试@20201123**\n\n\n总分:100.0分 考试时长:40分钟 总题量:20题\n\n\n考试说明: 1、考试时间40分钟 2、及格分数线为90分 3、祝各位考试顺利\n\n\n**单选题**\n\n\n1. 为了减少发布过程的出错率，公司要求发布人员根据上线程序清单，通过（）将程序部署至生产环境(本题\n分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nA selection interface with 4 radio button options: *手动* (Manual), *拷贝* (Copy), *批量拷贝* (Batch Copy), and *云管理平台* (Cloud Management Platform), where **云管理平台** is selected (filled blue radio button).  \n\n\n### Extracted Text  \n手动  \n拷贝  \n批量拷贝  \n云管理平台](#)\n\n\n\n2. 生产环境需求测试过程中，出现未测试通过的需求，下列做法正确的是（）(本题分数：5.0分)( 答案不确\n定)\n\n\n\n![### Summary  \nImage displays a multiple - choice (radio button) interface with 4 options for post - problem handling. The selected option is "回退该需求代码并进行回退测试" (Roll back the requirement code and perform rollback testing). Other options involve re - sending to release personnel, self - deploying via host login, or private communication with bureau staff.  \n\n\n### Extracted Text  \n1. 定位到问题后，对生产影响不大，重新发给发布人员进行上线  \n2. 定位到问题后，对生产影响不大，自己登录主机上线  \n3. 私自和局方人员沟通后上线  \n4. 回退该需求代码并进行回退测试](#)\n\n\n\n\n\n3. 在生产环境对上线内容进行测试，如果发现的问题影响了生产环境，此申请单内容（）(本题分数：5.0分)(\n\n答案不确定)\n\n\n\n![### Summary:  \nRadio button group with 4 Chinese options; "回退" (selected), "重新测试", "修改测试用例", "以上都正确".  \n\n\n### Extracted Text:  \n回退  \n重新测试  \n修改测试用例  \n以上都正确](#)\n\n\n\n\n\n4. 对生产上线后问题复盘，说法错误的是（）(本题分数：5.0分)( 答案不确定)\n\n\n分析上线过程中遇到的问题\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 1/5\n\n\n'),
         
    Document(
        metadata={'producer': 
                  'Skia/PDF m86',
                  'Skia/PDF m86', 
                  'creator': 
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 
                  'creationdate': '2020-11-23T02:03:36+00:00', 
                  'source': 'E:\\学习资料.pdf', 
                  'file_path': 'E:\\学习资料.pdf', 
                  'total_pages': 5, 'format': 'PDF 1.4', 
                  'title': '', 'author': '', 'subject': '', 'keywords': '', 'moddate': '2020-11-23T02:03:36+00:00', 'trapped': '', 'modDate': "D:20201123020336+00'00'", 
                  'creationDate': "D:20201123020336+00'00'", 
                  'page': 1}, 
        page_content='|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n|||分析上线测试过程中的问题<br>剩余时间:00:25:32|||\n|||分析具体原因并制定改进计划|分析具体原因并制定改进计划|分析具体原因并制定改进计划|\n|||问题复盘针对组长就可以了，开发人员不用参加|问题复盘针对组长就可以了，开发人员不用参加|问题复盘针对组长就可以了，开发人员不用参加|\n\n\n5. 生产环境上线过程中，局方要求修改与本次上线无关的代码文件你会怎么做（）(本题分数：5.0分)( 答案\n不确定)\n\n\n\n![### Summary:  \nA multiple - choice (radio button) interface in Chinese, with four options. The third option “上报项目经理和技术负责人进行评估” is selected (marked by a blue dot). The options relate to procedures for making modifications.  \n\n\n### Extracted Text:  \n1. 改动较小，没什么影响，直接修改  \n2. 和局方人员关系不错直接修改  \n3. 上报项目经理和技术负责人进行评估  \n4. 已上都不正确](#)\n\n\n\n6. 小丁是一名运维人员，局方找到他，要求他删除一条生产数据库中的错误数据，小丁的哪个做法是错误的\n（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nA selection interface with three radio button options (first selected) for handling a task: options relate to writing SQL to delete, contacting a manager, or writing SQL with approval and permission/account application.  \n\n\n### Extracted Text  \n- 比较简单，直接按照局方要求写sql语句删除  \n- 让局方人员直接找项目经理或者组长  \n- 写好sql语句并找组长进行审核，并按照流程申请权限、账号后进行操作](#)\n\n\n\n7. 生产上线测试过程中发现上线版本不正确，下列做法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nImage displays a radio button selection list (Chinese) with four options for code deployment/rollback actions; the third option ("通知发布人员回退本次上线代码") is selected (blue filled circle).  \n\n\n### Extracted Text  \n- 重新发一版本给发布人员上线  \n- 自己登录主机上线代码  \n- 通知发布人员回退本次上线代码  \n- 影响不大，暂时不管](#)\n\n\n\n8. 针对生产环境的操作，下面描述正确的是(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Image Summary:  \nA multiple - choice question about production environment operation procedures, with three options. The third option (stating that operation and maintenance personnel need to submit an application and can operate the production environment only after approval) is selected (marked with a blue filled - circle), while the first two options (stating that a project manager can directly authorize operation and maintenance personnel to operate without the permission of the authority and that an operation and maintenance team leader can directly operate in the production environment without applying respectively) are unselected (marked with empty circles).  \n\n\n### Extracted Text:  \n- 未经局方许可，项目经理可以直接赋权给运维人员进行操作  \n- 不用申请，运维组长可以直接在生产环境上进行操作  \n- 运维人员需要提交申请，审核通过后方可操作生产环境](#)\n\n\n\n\n\n9. 关于上线评审会的描述，不正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n上线评审会只对上线需求范围做审核\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 2/5\n\n\n'), 
    Document(metadata={'producer': 'Skia/PDF m86', 'creator': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 'creationdate': '2020-11-23T02:03:36+00:00', 'source': 'E:\\学习资料.pdf', 'file_path': 'E:\\学习资料.pdf', 'total_pages': 5, 'format': 'PDF 1.4', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'moddate': '2020-11-23T02:03:36+00:00', 'trapped': '', 'modDate': "D:20201123020336+00'00'", 'creationDate': "D:20201123020336+00'00'", 'page': 2}, page_content='|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n|||会中对上线需求的各种文档和存在的风险进行评审<br>剩余时间:00:25:32|||\n|||会中对上线需求范围进行评审|会中对上线需求范围进行评审|会中对上线需求范围进行评审|\n|||会中对上线所需资源进行评审|会中对上线所需资源进行评审|会中对上线所需资源进行评审|\n\n\n10. 关于上线前代码是否需要安全扫描说法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nA multiple - choice question (in Chinese) about code scanning for different deployment types (emergency/normal), with the selected option being "以上都不正确" (None of the above). The options are about whether emergency/normal/non - emergency deployed code needs scanning.  \n\n### Extracted Text  \n1. 紧急上线的代码不需要扫描  \n2. 正常上线的代码不需要扫描代码  \n3. 非紧急上线的代码需要代码扫描，紧急上线的代码不需要扫描  \n4. 以上都不正确](#)\n\n\n\n11. 账号申请成功之后可登陆生产环境，以下对生产环境操作描述正确的是（）(本题分数：5.0分)( 答案不\n确定)\n\n\n\n![### Summary (Optimized for Retrieval)  \nThe image displays a radio - button selection interface with four options. The options cover operations on production hosts (verification via `hostname -i` and `pwd`), approval procedures for operation - and - maintenance tasks, and restrictions on crontab operations. The last option "以上都正确" (All of the above are correct) is selected.  \n\n\n### Extracted Text  \n- 在生产主机上操作，需用hostname - i确认是否是该生产主机。pwd确认是否是所在的目录  \n- 根据项目，需求，运维实际操作需求，提供操作命令列表，方式。需要对应接口人审核后方可进行操作  \n- 未经对应负责人同意，禁止停启crontab任务或进程  \n- 以上都正确](#)\n\n\n\n\n\n12. 关于生产环境扫描出来的漏洞解决方法正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nA multiple - choice interface with 4 options related to vulnerability handling; the second option ("安全负责人和技术负责人制定漏洞方案，给出上线时间") is selected.  \n\n### Extracted Text  \n1. 不影响生产业务办理，暂时不用修改  \n2. 安全负责人和技术负责人制定漏洞方案，给出上线时间  \n3. 没有人通过漏洞攻击系统，暂时不用管  \n4. 以上说法都不正确](#)\n\n\n\n\n\n13. 生产上线过程中对某些文件没有操作权限的情况，以下做法正确的是（）(本题分数：5.0分)( 答案不确\n定)\n\n\n\n![### 图像总结  \n4个单选操作选项（涉及root用户切换、权限赋权、上报权限申请），**“上报组长和项目经理，等待权限申请后操作上线”**被选中。  \n\n### 提取文本  \n- 当前用户切换到root用户执行  \n- 当前用户切换到root用户，给当前用户赋权  \n- 使用本机其他用户，尝试进行权限赋权等操作  \n- 上报组长和项目经理，等待权限申请后操作上线](#)\n\n\n\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 3/5\n\n\n'), 
    Document(metadata={'producer': 'Skia/PDF m86', 'creator': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 'creationdate': '2020-11-23T02:03:36+00:00', 'source': 'E:\\学习资料.pdf', 'file_path': 'E:\\学习资料.pdf', 'total_pages': 5, 'format': 'PDF 1.4', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'moddate': '2020-11-23T02:03:36+00:00', 'trapped': '', 'modDate': "D:20201123020336+00'00'", 'creationDate': "D:20201123020336+00'00'", 'page': 3}, page_content='账号、申请人、同意人、开始时间、结束时间、事由\n\n|Col1|020/11/23 【全员学习】生产环境操作规范考试@20201123|Col3|\n|---|---|---|\n||14.小张入职不足一年，生产环境当晚需要重启服务，他的做法错误的是（）(本题分数：5.0分)(<br>答案不确<br>定)<br>剩余时间:00:25:32||\n||15.关于生产环境操作哪个描述是正确的（）(本题分数：5.0分)(<br>答案不确定)<br>16.生产系统权限申请表包括那些内容（）(本题分数：5.0分)(<br>答案不确定)<br>听从组长安排<br>自己直接重启服务<br>组长和项目经理审批通过，小张重启服务<br>上报组长和项目经理，等待授权后操作<br>未经对应负责人同意禁止运行sqlplus数据库命令<br>未经对应负责人同意禁止修改环境变量<br>未经对应负责人同意禁止在生产环境做程序测试工作<br>以上都正确<br>账号、申请人、同意人<br>账号、申请人、同意人、开始时间、结束时间<br>||\n\n\n\n账号、同意人、开始时间、结束时间、事由、上线时间\n\n\n17. 需求上线当晚，测试过程中发现生产有一个问题，开发人员判断修改生产数据库原有的一个参数配置即\n可。此时发布人员应该（）(本题分数：5.0分)( 答案不确定)\n\n\n\n![### Summary  \nThree radio button options (Chinese); the middle option "上报给组长和项目经理" is selected. Options: "立即修改" (unselected), "上报给组长和项目经理" (selected), "提供账号给开发人员，让开发人员自己修改" (unselected).  \n\n\n### Extracted Text  \n立即修改  \n上报给组长和项目经理  \n提供账号给开发人员，让开发人员自己修改](#)\n\n\n\n18. 对生产扫描出来的安全漏洞理解正确的是（）(本题分数：5.0分)( 答案不确定)\n\n\n简单的漏洞可以直接在生产上修复\n\n\n低级漏洞不修改\n\n\n需要在测试环境上验证通过后才能上线生产环境\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 4/5\n\n\n'), 
    Document(metadata={'producer': 'Skia/PDF m86', 'creator': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36', 'creationdate': '2020-11-23T02:03:36+00:00', 'source': 'E:\\学习资料.pdf', 'file_path': 'E:\\学习资料.pdf', 'total_pages': 5, 'format': 'PDF 1.4', 'title': '', 'author': '', 'subject': '', 'keywords': '', 'moddate': '2020-11-23T02:03:36+00:00', 'trapped': '', 'modDate': "D:20201123020336+00'00'", 'creationDate': "D:20201123020336+00'00'", 'page': 4}, page_content='|Col1|020/11/2|3 【全员学习】生产环境操作规范考试@20201123|Col4|Col5|\n|---|---|---|---|---|\n||解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32|解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32|解决安全漏洞的顺序是按照漏洞级别从低到高解决<br>剩余时间:00:25:32||\n||19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|19.关于生产环境上出现紧急问题时以及紧急上线处理，开发人员正确的操作是（）(本题分数：5.0分)(<br>答<br>案不确定)<br>20.关于生产发布时 需要上线脚本的情况，以下说法错误的是（）(本题分数：5.0分)(<br>答案不确定)<br>提交试卷<br>临时保存<br>检查答卷<br>影响生产，直接修改上线<br>原地等待，暂时不管<br>定位检查生产问题并通知项目经理，等待上线通知<br>以上说法都不正确<br>需要组长审核后发给用户<br>要求用户来执行<br>用户不在的情况下自己执行<br>用户不在的情况下先通知项目经理与用户沟通|\n\n\ntraining.si-tech.com.cn/exam/portal/examPage.html?examId=13573&phoneFlag=sitech2018 5/5\n\n\n')]

"""