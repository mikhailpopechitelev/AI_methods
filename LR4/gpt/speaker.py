from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import START, MessagesState, StateGraph




class Speaker:
    def __init__(self,thread_id, gptToken) -> None:

        self.model = GigaChat(
            credentials=gptToken,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
        )


        self.messages = [
            SystemMessage(
                content="Ты — музыкальный критик, глубоко разбирающийся в музыке разных жанров, эпох и культур. "
                        "К тебе обращаются пользователи, чтобы получить рецензию или твое личное мнение по поводу той или иной композиции, альбома или исполнителя. "
                        "Отвечай на поставленные вопросы пользователей. Формат должен быть таким, чтобы он не был слишком длинным и не казался пользователю ответом от машины." 
                        "Используй четкие и лаконичные формулировки, пиши уверенным, но дружелюбным тоном, добавляя при необходимости немного эмоций, чтобы оживить ответ."
            )
        ]
        
        # Инициализация состояния графа
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model", self.call_model)

        # Инициализация памяти
        self.serializer = JsonPlusSerializer()
        self.memory = MemorySaver(serde=self.serializer)
        self.app = self.workflow.compile(checkpointer=self.memory)

        # Дополнительные конфигурации (например, thread_id)
        self.config = {"configurable": {"thread_id": f'{thread_id}'}}        
        
    def call_model(self, state: dict) -> dict:
        
        response = self.model.invoke(state["messages"])
        return {"messages": response}
    
    def send_message(self, query: str) -> str:
        
        # Добавляем сообщение от пользователя в контекст
        input_messages = [HumanMessage(content=query)]
        self.messages.append(input_messages[0])

        # Отправляем запрос в модель
        output = self.app.invoke({"messages": self.messages}, self.config)

        # Получаем ответ от модели и добавляем его в контекст
        response_content = output["messages"][-1].content
        self.messages.append(response_content)

        self.serializer.dumps
        return response_content