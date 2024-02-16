from io import BytesIO
import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_QEMAOAPI = "http://api.qemao.com/api/" 

@plugins.register(name="erciyuan_pic",
                  desc="erciyuan_pic插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class erciyuan_pic(Plugin):
    content = None
    config_data = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f""
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        
        if self.content == "二次元":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__),"config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return 
            
            reply = Reply()
            result = self.erciyuan_pic()
            if result != None:
                reply.type = ReplyType.IMAGE if isinstance(result,BytesIO) else ReplyType.IMAGE_URL
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def erciyuan_pic(self):
        url = BASE_URL_QEMAOAPI + "acgn/"
        params = f"type={self.config_data['erciyuan_pic_size']}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        try:
            response = requests.get(url=url, params=params, headers=headers)
            if response.status_code==200:
                logger.info(f"获取二次元成功,返回的数据前10字节为：{response.content[:10]}")
                image_bytes = response.content
                # 使用BytesIO保存到内存中
                image_in_memory = BytesIO(image_bytes)
                return image_in_memory
            else:
                logger.error(f"获取二次元失败，返回的状态码为：{response.status_code}")
        except Exception as e:
            logger.error(f"获取二次元抛出异常:{e}")

        logger.error("所有接口都挂了,无法获取")
        return None
