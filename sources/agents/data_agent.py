import asyncio
import platform
import os

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.PyInterpreter import PyInterpreter
from sources.tools.SaveTool import HTMLSaveTool, CSSSaveTool, JSSaveTool, SQLSaveTool
from sources.memory import Memory
from sources.logger import Logger


class DataAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "python": PyInterpreter(),
            "bash": BashInterpreter(),
            "html": HTMLSaveTool(),
            "css": CSSSaveTool(),
            "javascript": JSSaveTool(),
            "sql": SQLSaveTool(),
            "file_finder": FileFinder()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "data"
        self.type = "data_agent"
        self.logger = Logger("data_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                             recover_last_session=False,
                             memory_compression=False,
                             model_provider=provider.get_model_name())

    def _is_save_only_language(self, name: str) -> bool:
        return name in ('html', 'css', 'javascript', 'sql')

    def add_sys_info_prompt(self, prompt):
        info = (
            f"System Info:\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            f"Direktori kerja: {self.work_dir}\n"
            f"Mode: Data Agent - Analisis data dan visualisasi\n"
            f"Library Python: csv, json, sqlite3, statistics, math, collections, itertools\n"
            f"Visualisasi: Chart.js via HTML, tabel HTML, dashboard\n"
            f"INSTRUKSI: Langsung analisis. Jangan bertanya. Berikan insight dari data.\n"
            f"Simpan file dengan format ```bahasa:namafile\n"
            f"JANGAN tulis app.run() atau server. Port 5000 sudah digunakan."
        )
        return f"{prompt}\n\n{info}"

    async def process(self, prompt, speech_module) -> str:
        exec_success = False
        attempt = 0
        max_attempts = 5
        prompt = self.add_sys_info_prompt(prompt)
        self.memory.push('user', prompt)

        while not exec_success and attempt < max_attempts and not self.stop:
            self.logger.info(f"Data analysis attempt {attempt + 1}/{max_attempts}")
            animate_thinking("Analyzing data...", color="status")
            self.status_message = f"📊 Menganalisis data... (percobaan {attempt + 1}/{max_attempts})"
            await self.wait_message(speech_module)
            answer, reasoning = await self.llm_request()
            self.last_reasoning = reasoning

            if "```" not in answer:
                self.last_answer = answer
                exec_success = True
                break

            self.show_answer()
            exec_success, feedback = self.execute_modules(answer)
            answer = self.remove_blocks(answer)
            self.last_answer = answer

            if not exec_success:
                pretty_print(f"Data execution issue: {feedback}", color="warning")
                self.memory.push('user',
                    f"Ada masalah: {feedback}\n"
                    f"Perbaiki dan coba lagi. Gunakan library standar Python saja."
                )
                attempt += 1

        self.status_message = "Siap"
        return self.last_answer, self.last_reasoning


if __name__ == "__main__":
    pass
