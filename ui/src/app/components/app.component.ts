import {Component, OnDestroy, OnInit} from '@angular/core';
import {Link} from "../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy  {

  constructor(private router: Router,
              private route: ActivatedRoute) {
  }

  links: Link[] = [];

  ngOnDestroy(): void {
      console.log("Method not implemented.");
  }

  ngOnInit(): void {
    this.initLinks()
  }

  navigate(navigationPath: string) {
    this.activateCurrentLink(navigationPath);
    this.router.navigate([navigationPath], {relativeTo: this.route});
  }

  private activateCurrentLink(navigationPath?: string) {

    if (navigationPath?.length === 0) {
      navigationPath = 'HOME';
    }

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
    this.addLink("HOME", "house-fill","house", true, "#37c9fb", "#738893");
    this.addLink("STATISTICS",  "speedometer2","speedometer2",false, "#fd2a2a", "#a57777");
    this.activateCurrentLink("HOME");
  }

  private addLink(name: string, iconActive:string, iconInactive:string, active: boolean, activeColor:string, inactiveColor: string) {
    let link:Link = new Link();
    link.name = name;
    link.iconActive = iconActive;
    link.iconInactive = iconInactive;
    link.active = active;
    link.activeColor = activeColor;
    link.inactiveColor = inactiveColor;
    this.links.push(link)
  }


}
