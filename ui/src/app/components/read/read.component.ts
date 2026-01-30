import {Component, OnInit} from '@angular/core';
import {OllamaService} from "../../services/ollama.service";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-read',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    NgIf,
    NgForOf
  ],
  templateUrl: './read.component.html',
  styleUrl: './read.component.scss'
})
export class ReadComponent implements OnInit {
  importText = new FormControl('', { nonNullable: true })
  text = new FormControl('', { nonNullable: true })
  mostImportantWord = ""
  simplifiedText = ""
  loading: boolean = false;
  tokensDifficulty: any[] = []

  constructor(private ollama:OllamaService ) {}

  ngOnInit(): void {
    this.importText.setValue("Утром я готовлю завтрак.\n" +
      "Я беру яйца и готовлю яичницу.\n" +
      "Яйца жарятся быстро и вкусно пахнут.\n" +
      "Потом я делаю кофе.\n" +
      "Кофе горячий и ароматный.\n" +
      "Я сажусь за стол и ем завтрак.\n" +
      "Завтрак с яйцами и кофе очень вкусный.\n" +
      "Так приятно начинать утро с хорошего завтрака.")
  }


  saveText() {
    console.log("saveText: " + this.importText.value);
    this.text.setValue(this.importText.value);
  }

  mostImportantWords() {
    this.loading = true;

    let question = `Take from this text the most important words and return it as a comma-separated list (only the most important words and avoid comments and other stuff): \n\n${this.text.value}`;

    this.ollama.chat(question,'').subscribe(response => {
      console.log("Ollama response: ", response);
      this.mostImportantWord = response;
      this.loading = false;
    });
  }

  generateSimplerText() {
    this.loading = true;

    let question = `Simplify this text: \n\n${this.text.value}`;

    this.ollama.chat(question,'You are very good in simplifying text in its own language').subscribe(response => {
      console.log("Ollama response: ", response);
      this.simplifiedText = response;
      this.loading = false;
    });
  }

  evaluateDifficulty() {
    this.loading = true;

    let question = `Return ONLY JSON matching this schema:
{"tokens":[{"value":"string","type":"word|punct","difficulty":"A1|A2|B1|B2|C1|C2|null","translationEN":"string"}]}

Rules:
- Tokenize into words and punctuation.
- Include spaces as type "ws" OR do not include spaces (choose ONE and be consistent).
- difficulty is only for type=word, else null. Evaluate difficulty according to CEFR levels.
- translationEN is only for type=word, else empty string. Always translate to English.
Text: \n\n${this.text.value}`;

    this.ollama.chat(question,'You are a JSON API. Output MUST be valid JSON only. No markdown, no code fences, no explanations.').subscribe(response => {
      console.log("Ollama response: ", response);

      this.tokensDifficulty = this.extractJsonFromModelOutput(response);
      this.loading = false;
    });
  }

  extractJsonFromModelOutput(raw: string): any {
    if (!raw) throw new Error('Empty model response');

    // Remove common wrappers that break parsing
    const cleaned = raw
      .replace(/```json|```/g, '')
      .replace(/\\boxed\s*\{/g, '{')
      .trim();

    // Find first JSON object/array start
    const firstObj = cleaned.indexOf('{');
    const firstArr = cleaned.indexOf('[');
    let start = -1;
    if (firstObj === -1) start = firstArr;
    else if (firstArr === -1) start = firstObj;
    else start = Math.min(firstObj, firstArr);

    if (start === -1) throw new Error('No JSON start found');

    // Try progressively shorter suffixes until parse works
    for (let end = cleaned.length; end > start; end--) {
      const chunk = cleaned.slice(start, end).trim();
      try {
        return JSON.parse(chunk);
      } catch { /* keep trying */ }
    }

    throw new Error('Could not parse JSON from model output');
  }

}
