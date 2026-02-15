import asyncio
import platform
import os

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.searxSearch import searxSearch
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.PyInterpreter import PyInterpreter
from sources.tools.SaveTool import HTMLSaveTool
from sources.memory import Memory
from sources.logger import Logger


class ResearchAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        super().__init__(name, prompt_path, provider, verbose, browser)
        self.tools = {
            "web_search": searxSearch(),
            "bash": BashInterpreter(),
            "python": PyInterpreter(),
            "html": HTMLSaveTool(),
            "file_finder": FileFinder()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "research"
        self.type = "research_agent"
        self.logger = Logger("research_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                             recover_last_session=False,
                             memory_compression=False,
                             model_provider=provider.get_model_name())
        self.research_notes = []

    def add_sys_info_prompt(self, prompt):
        info = (
            f"System Info:\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"Direktori kerja: {self.work_dir}\n"
            f"Mode: Research Agent - Riset mendalam dan analisis\n"
            f"Tools: web_search, bash, python, html (simpan laporan), file_finder\n"
            f"INSTRUKSI: Langsung lakukan riset. Jangan bertanya. Kumpulkan data dari multiple sources.\n"
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
            self.logger.info(f"Research attempt {attempt + 1}/{max_attempts}")
            animate_thinking("Researching...", color="status")
            self.status_message = f"🔬 Melakukan riset... (percobaan {attempt + 1}/{max_attempts})"
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
                pretty_print(f"Research execution issue: {feedback}", color="warning")
                self.memory.push('user',
                    f"Ada masalah eksekusi: {feedback}\n"
                    f"Perbaiki dan coba lagi. Jangan ulangi error yang sama."
                )
                attempt += 1

        self.status_message = "Siap"
        return self.last_answer, self.last_reasoning


if __name__ == "__main__":
    pass
