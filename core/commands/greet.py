"""
path: core/commands/greet.py
purpose: Implements a greeting command with customizable options
critical:
- Demonstrates command parameters
- Uses base command class
- Shows choices and descriptions
"""

import random
import discord
from discord import app_commands
from typing import Optional
from .base import BaseCommand
from ..command_registry import registry

class GreetCommand(BaseCommand):
    """Command to greet users with customizable options."""
    
    def __init__(self):
        """Initialize the greet command."""
        super().__init__(
            name="greet",
            description="Get a customized greeting from the bot"
        )
        
        # Set a cooldown of 5 seconds
        self.cooldown = 5
        
    def to_app_command(self) -> app_commands.Command:
        """
        Convert to Discord application command with parameters.
        
        Returns:
            The Discord application command
        """
        @app_commands.describe(
            style="The style of greeting to use",
            language="The language to greet in",
            private="Whether to send the greeting privately"
        )
        @app_commands.choices(
            style=[
                app_commands.Choice(name="Casual", value="casual"),
                app_commands.Choice(name="Formal", value="formal"),
                app_commands.Choice(name="Funny", value="funny")
            ],
            language=[
                app_commands.Choice(name="English", value="en"),
                app_commands.Choice(name="Spanish", value="es"),
                app_commands.Choice(name="French", value="fr")
            ]
        )
        async def command_callback(
            interaction: discord.Interaction,
            style: str = "casual",
            language: str = "en",
            private: bool = False
        ) -> None:
            await self.execute(
                interaction,
                style=style,
                language=language,
                private=private
            )
            
        return app_commands.Command(
            name=self.name,
            description=self.description,
            callback=command_callback
        )
        
    async def execute(
        self,
        interaction: discord.Interaction,
        style: str = "casual",
        language: str = "en",
        private: bool = False,
        **kwargs
    ) -> None:
        """
        Execute the greet command.
        
        Args:
            interaction: The Discord interaction
            style: The greeting style (casual, formal, funny)
            language: The greeting language (en, es, fr)
            private: Whether to send privately
            **kwargs: Additional arguments (unused)
        """
        try:
            # Get appropriate greetings based on style and language
            greetings = self._get_greetings(style, language)
            
            # Select random greeting
            greeting = random.choice(greetings).format(
                name=interaction.user.display_name
            )
            
            # Send response
            await interaction.response.send_message(
                greeting,
                ephemeral=private
            )
            
        except Exception as e:
            await self.handle_error(interaction, e)
            
    def _get_greetings(self, style: str, language: str) -> list[str]:
        """
        Get list of appropriate greetings.
        
        Args:
            style: The greeting style
            language: The greeting language
            
        Returns:
            List of greeting templates
        """
        greetings = {
            "en": {
                "casual": [
                    "Hey {name}! What's up?",
                    "Hi {name}! How's it going?",
                    "Hello {name}! Nice to see you!"
                ],
                "formal": [
                    "Good day, {name}. How may I assist you?",
                    "Greetings, {name}. Welcome to our server.",
                    "Welcome, {name}. How may I be of service?"
                ],
                "funny": [
                    "Yo {name}! Ready to rock and roll? 🎸",
                    "What's cookin', {name}? 🍳",
                    "Look who decided to show up! It's {name}! 🎉"
                ]
            },
            "es": {
                "casual": [
                    "¡Hola {name}! ¿Qué tal?",
                    "¡Hey {name}! ¿Cómo estás?",
                    "¡Hola {name}! ¡Qué bueno verte!"
                ],
                "formal": [
                    "Buenos días, {name}. ¿En qué puedo ayudarle?",
                    "Saludos, {name}. Bienvenido a nuestro servidor.",
                    "Bienvenido, {name}. ¿En qué puedo servirle?"
                ],
                "funny": [
                    "¡Qué pasa {name}! ¿Listo para la fiesta? 🎉",
                    "¡Mira quién llegó! ¡Es {name}! 🌟",
                    "¡Hola {name}! ¿Listo para la diversión? 🎮"
                ]
            },
            "fr": {
                "casual": [
                    "Salut {name}! Ça va?",
                    "Coucou {name}! Comment ça va?",
                    "Hey {name}! Content de te voir!"
                ],
                "formal": [
                    "Bonjour {name}. Comment puis-je vous aider?",
                    "Salutations, {name}. Bienvenue sur notre serveur.",
                    "Bienvenue, {name}. En quoi puis-je vous être utile?"
                ],
                "funny": [
                    "Yo {name}! Prêt à faire la fête? 🎉",
                    "Regarde qui voilà! C'est {name}! 🌟",
                    "Salut {name}! On s'amuse? 🎮"
                ]
            }
        }
        
        return greetings.get(language, greetings["en"]).get(style, greetings[language]["casual"])

# Register the command
registry.register_command(GreetCommand()) 