import asyncio
import platform
import os

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.fileFinder import FileFinder
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.SaveTool import HTMLSaveTool, CSSSaveTool, JSSaveTool
from sources.memory import Memory
from sources.logger import Logger


class DesignAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "html": HTMLSaveTool(),
            "css": CSSSaveTool(),
            "javascript": JSSaveTool(),
            "bash": BashInterpreter(),
            "file_finder": FileFinder()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "design"
        self.type = "design_agent"
        self.logger = Logger("design_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                             recover_last_session=False,
                             memory_compression=False,
                             model_provider=provider.get_model_name())

    def add_sys_info_prompt(self, prompt):
        info = (
            f"System Info:\n"
            f"Direktori kerja: {self.work_dir}\n"
            f"Mode: Design Agent - UI/UX & Visual Design Specialist\n"
            f"Output: HTML + CSS + JavaScript files\n"
            f"CDN tersedia: Google Fonts, Font Awesome, Chart.js, Animate.css\n"
            f"INSTRUKSI: Langsung buat design. Jangan bertanya.\n"
            f"Buat HTML lengkap dengan CSS inline atau file terpisah.\n"
            f"Simpan file dengan format ```bahasa:namafile\n"
            f"JANGAN tulis app.run() atau server. Port 5000 sudah digunakan.\n"
            f"SELALU buat design yang responsive dan modern."
        )
        return f"{prompt}\n\n{info}"

    async def process(self, prompt, speech_module) -> str:
        exec_success = False
        attempt = 0
        max_attempts = 5
        prompt = self.add_sys_info_prompt(prompt)
        self.memory.push('user', prompt)

        while not exec_success and attempt < max_attempts and not self.stop:
            self.logger.info(f"Design attempt {attempt + 1}/{max_attempts}")
            animate_thinking("Designing...", color="status")
            self.status_message = f"🎨 Mendesain... (percobaan {attempt + 1}/{max_attempts})"
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
                pretty_print(f"Design execution issue: {feedback}", color="warning")
                self.memory.push('user',
                    f"Ada masalah: {feedback}\n"
                    f"Perbaiki dan coba lagi."
                )
                attempt += 1

        self.status_message = "Siap"
        return self.last_answer, self.last_reasoning


if __name__ == "__main__":
    pass
