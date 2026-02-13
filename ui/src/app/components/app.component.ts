import {Component, OnDestroy, OnInit} from '@angular/core';
import {Link} from "../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";
import {ImparaService} from "../services/impara.service";
import {User} from "../domains/User";
import {Language} from "../domains/Language";
import {Languages} from "../domains/Languages";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  user: User | null = null // synchronized with ImparaService.user$
  userLanguage: Language | null = null // synchronized
  languages: Languages[] = []

  constructor(private router: Router,
              private route: ActivatedRoute,
              private imparaService: ImparaService) {
  }

  links: Link[] = [];

  ngOnInit(): void {
    this.imparaService.listLanguages().subscribe( languages => { this.languages = languages })
    this.imparaService.user$.subscribe( user => {this.user = user})
    this.initLinks()
    let currentUser = localStorage.getItem("currentUser")
    if (currentUser) {
      console.log("CURRENT USER EXIST")
      this.user = JSON.parse(currentUser)
      let language = localStorage.getItem("currentLanguage")
      if (language) {
        console.log("CURRENT LANGUAGE EXIST")
        const parsedLanguage: Language = JSON.parse(language);
        this.imparaService.setUserLanguage(parsedLanguage);
      }
      this.imparaService.language$.subscribe( language => {
        this.userLanguage = language
      })
    }
  }

  navigate(navigationPath: string) {
    this.activateCurrentLink(navigationPath);
    this.router.navigate([navigationPath], {relativeTo: this.route});
  }

  private activateCurrentLink(navigationPath?: string) {

    console.log("activateCurrentLink: " + navigationPath);

    if (navigationPath?.length === 0) {
      navigationPath = 'HOME';
    }

    navigationPath = navigationPath?.replace("#", "")

    this.links.forEach(link => {
      if (link.name === navigationPath) {
        link.active = true;
        link.color = link.activeColor;
      } else {
        link.active = false;
        link.color = link.inactiveColor;
      }
    });
  }

  private initLinks() {
    this.addLink("HOME", "house-fill", "house", true, "#37c9fb", "#738893");
    this.addLink("READ", "book-half", "book", true, "#41ff0f", "#4e7344");
    this.addLink("STATISTICS", "speedometer2", "speedometer2", false, "#fd2a2a", "#a57777");

    let href = document.location.href;
    if (href.indexOf("#") > 0) {
      let parts = href.split("/");
      let navigationPath = parts[parts.length - 1].toUpperCase();
      this.activateCurrentLink(navigationPath);
    } else {
      this.activateCurrentLink("HOME");
    }
  }

  private addLink(name: string, iconActive: string, iconInactive: string, active: boolean, activeColor: string, inactiveColor: string) {
    let link: Link = new Link();
    link.name = name;
    link.iconActive = iconActive;
    link.iconInactive = iconInactive;
    link.active = active;
    link.activeColor = activeColor;
    link.inactiveColor = inactiveColor;
    this.links.push(link)
  }


  logout() {
    this.imparaService.logout()
  }

  getLanguageName(code: string): string | undefined {
    return this.languages.find(lang => lang.code === code)?.name;
  }
}
