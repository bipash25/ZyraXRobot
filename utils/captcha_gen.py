"""
Captcha generation utilities for ZyraX Bot
"""
import random
import string
from typing import Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import io

class CaptchaGenerator:
    """Generate different types of captcha challenges"""
    
    @staticmethod
    def generate_math_captcha() -> Tuple[str, str]:
        """
        Generate a simple math captcha
        
        Returns:
            Tuple of (question, answer)
        """
        operations = ['+', '-', '*']
        operation = random.choice(operations)
        
        if operation == '+':
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            answer = a + b
            question = f"What is {a} + {b}?"
        elif operation == '-':
            a = random.randint(10, 100)
            b = random.randint(1, a - 1)
            answer = a - b
            question = f"What is {a} - {b}?"
        else:  # multiplication
            a = random.randint(1, 12)
            b = random.randint(1, 12)
            answer = a * b
            question = f"What is {a} × {b}?"
        
        return question, str(answer)
    
    @staticmethod
    def generate_text_captcha() -> Tuple[str, str]:
        """
        Generate a text-based captcha
        
        Returns:
            Tuple of (question, answer)
        """
        # Generate random string
        length = random.randint(4, 6)
        answer = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        question = f"Type this text: `{answer}`"
        
        return question, answer
    
    @staticmethod
    def generate_button_captcha() -> Tuple[str, str, Dict[str, Any]]:
        """
        Generate button-based captcha
        
        Returns:
            Tuple of (question, correct_answer, buttons_data)
        """
        # Generate random number for correct answer
        correct = random.randint(1000, 9999)
        
        # Generate wrong answers
        wrong_answers = []
        while len(wrong_answers) < 3:
            wrong = random.randint(1000, 9999)
            if wrong != correct and wrong not in wrong_answers:
                wrong_answers.append(wrong)
        
        # Shuffle answers
        all_answers = [correct] + wrong_answers
        random.shuffle(all_answers)
        
        question = f"Click the button with the number: **{correct}**"
        
        buttons_data = {
            'answers': all_answers,
            'correct': correct
        }
        
        return question, str(correct), buttons_data
    
    @staticmethod
    def generate_image_captcha(text: str = None) -> Tuple[bytes, str]:
        """
        Generate image-based captcha
        
        Args:
            text: Text to render (if None, generates random)
            
        Returns:
            Tuple of (image_bytes, text_answer)
        """
        if text is None:
            text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        
        # Create image
        width, height = 200, 80
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Add some noise lines
        for _ in range(random.randint(3, 7)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)
        
        # Add text with slight rotation and positioning
        text_width = draw.textlength(text, font=font)
        x = (width - text_width) // 2 + random.randint(-10, 10)
        y = (height - 24) // 2 + random.randint(-5, 5)
        
        # Add text with random color
        color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        draw.text((x, y), text, fill=color, font=font)
        
        # Add some noise dots
        for _ in range(random.randint(50, 100)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill='lightgray')
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        return img_bytes, text
    
    @staticmethod
    def generate_emoji_captcha() -> Tuple[str, str]:
        """
        Generate emoji-based captcha
        
        Returns:
            Tuple of (question, answer)
        """
        emojis = ['🍎', '🍌', '🍊', '🍇', '🍓', '🥝', '🍑', '🥭', '🍍', '🥥']
        target_emoji = random.choice(emojis)
        
        # Create a sequence with the target emoji
        sequence_length = random.randint(8, 12)
        sequence = []
        target_count = random.randint(2, 4)
        
        # Add target emojis
        for _ in range(target_count):
            sequence.append(target_emoji)
        
        # Fill rest with random emojis
        while len(sequence) < sequence_length:
            other_emoji = random.choice([e for e in emojis if e != target_emoji])
            sequence.append(other_emoji)
        
        # Shuffle the sequence
        random.shuffle(sequence)
        
        sequence_str = ''.join(sequence)
        question = f"How many {target_emoji} do you see?\n{sequence_str}"
        
        return question, str(target_count)
    
    @staticmethod
    def generate_captcha(captcha_type: str = "button") -> Dict[str, Any]:
        """
        Generate captcha of specified type
        
        Args:
            captcha_type: Type of captcha (button, math, text, image, emoji)
            
        Returns:
            Dict with captcha data
        """
        if captcha_type == "math":
            question, answer = CaptchaGenerator.generate_math_captcha()
            return {
                'type': 'math',
                'question': question,
                'answer': answer
            }
        
        elif captcha_type == "text":
            question, answer = CaptchaGenerator.generate_text_captcha()
            return {
                'type': 'text',
                'question': question,
                'answer': answer
            }
        
        elif captcha_type == "button":
            question, answer, buttons_data = CaptchaGenerator.generate_button_captcha()
            return {
                'type': 'button',
                'question': question,
                'answer': answer,
                'buttons': buttons_data
            }
        
        elif captcha_type == "image":
            image_bytes, answer = CaptchaGenerator.generate_image_captcha()
            return {
                'type': 'image',
                'question': "Enter the text shown in the image:",
                'answer': answer,
                'image': image_bytes
            }
        
        elif captcha_type == "emoji":
            question, answer = CaptchaGenerator.generate_emoji_captcha()
            return {
                'type': 'emoji',
                'question': question,
                'answer': answer
            }
        
        else:
            # Default to button captcha
            return CaptchaGenerator.generate_captcha("button")
