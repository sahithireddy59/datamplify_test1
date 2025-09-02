import { Injectable, OnDestroy} from '@angular/core';
import { Subject, BehaviorSubject, fromEvent } from 'rxjs';
import { takeUntil, debounceTime } from 'rxjs/operators';
import { Router } from '@angular/router';
import { ViewTemplateDrivenService } from '../../components/workbench/view-template-driven.service';

// Menu
export interface Menu {
  headTitle?: string;
  headTitle2?: string;
  path?: string;
  title?: string;
  icon?: string;
  type?: string;
  badgeValue?: string;
  badgeClass?: string;
  active?: boolean;
  selected?: boolean;
  bookmark?: boolean;
  children?: Menu[];
  children2?: Menu[];
  Menusub?: boolean;
  target?: boolean;
  menutype?:string;
  nochild?: any,
}
@Injectable({
  providedIn: 'root',
})
export class NavService implements OnDestroy {
  private unsubscriber: Subject<any> = new Subject();
  public screenWidth: BehaviorSubject<number> = new BehaviorSubject(
    window.innerWidth
  );

  // Search Box
  public search = false;

  // Language
  public language = false;

  // Mega Menu
  public megaMenu = false;
  public levelMenu = false;
  public megaMenuColapse: boolean = window.innerWidth < 1199 ? true : false;

  // Collapse Sidebar
  public collapseSidebar: boolean = window.innerWidth < 991 ? true : false;

  // For Horizontal Layout Mobile
  public horizontal: boolean = window.innerWidth < 991 ? false : true;

  // Full screen
  public fullScreen = false;
  active: any;

  constructor(private router: Router,private viewTemplate:ViewTemplateDrivenService) {
    this.setScreenWidth(window.innerWidth);
    fromEvent(window, 'resize')
      .pipe(debounceTime(1000), takeUntil(this.unsubscriber))
      .subscribe((evt: any) => {
        this.setScreenWidth(evt.target.innerWidth);
        if (evt.target.innerWidth < 991) {
          this.collapseSidebar = true;
          this.megaMenu = false;
          this.levelMenu = false;
        }
        if (evt.target.innerWidth < 1199) {
          this.megaMenuColapse = true;
        }
      });
    if (window.innerWidth < 991) {
      // Detect Route change sidebar close
      this.router.events.subscribe((event) => {
        this.collapseSidebar = true;
        this.megaMenu = false;
        this.levelMenu = false;
      });
    }
  }
  ngOnDestroy() {
    this.unsubscriber.next;
    this.unsubscriber.complete();
  }

  private setScreenWidth(width: number): void {
    this.screenWidth.next(width);
  }

  MENUITEMS: Menu[] = [
    // Dashboard
  //   { headTitle: 'MAIN' },
  //   {
  //     title: 'Dashboard',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"></path>
  // </svg>`,
  //     type: 'link',
  //     active: false,
  //     nochild: true,
  //     path:"/dashboard"
    
  //   },
    // { headTitle: 'Server' },
    {
  //     title: 'SQL',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="side-menu__icon">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M11.99 18.54l-7.37-5.73L3 14.07l9 7 9-7-1.63-1.27zM12 16l7.36-5.73L21 9l-9-7-9 7 1.63 1.27L12 16zm0-11.47L17.74 9 12 13.47 6.26 9 12 4.53z">
  //     </path>
  // </svg>`,
  //     type: 'sub',
  //     type: 'link',
  //     active: false,
  //    children: [
  //       {
  //         title: 'Profile',
  //         type: 'link',
  //         active: false,
  //         path:'/pages/profile'
         
  //       },
  //       {
  //         title: 'Notification List',
  //         type: 'link',
  //         active: false,
  //         path:"/pages/notification-list"
        
  //       },
  //       {
  //         title: 'Mail Inbox',
  //         type: 'link',
  //         active: false,
  //         path:"/pages/mail-inbox"
        
  //       },
  //       {
  //         title: 'Gallery',
  //         type: 'link',
  //         active: false,
  //         path:"/pages/gallery"
        
  //       },
  //       {
  //         title: 'Extension',
  //         type: 'sub',
  //         active: false,
  //         selected:false,
  //         children: [
  //           { path: '/pages/extension/about-company', title: 'About Company', type: 'link' },
  //           { path: '/pages/extension/faqs', title: 'FAQS', type: 'link' },
  //           { path: '/pages/extension/terms', title: 'Terms', type: 'link' },
  //           { path: '/pages/extension/invoice', title: 'Invoice', type: 'link' },
  //           { path: '/pages/extension/pricing-tables', title: 'Pricing Tables', type: 'link' },
  //           { path: '/pages/extension/settings', title: 'Settings', type: 'link' },
  //           { path: '/pages/extension/blog', title: 'Blog', type: 'link' },
  //           { path: '/pages/extension/blog-details', title: 'Blog Details', type: 'link' },
  //           { path: '/pages/extension/blog-post', title: 'Blog Post', type: 'link' },
  //           { path: '/pages/extension/empty-page', title: 'Empty Page', type: 'link' },
  //         ],
  //       },
  //       {
  //         title: 'File Manager',
  //         type: 'sub',
  //         Menusub: true,
  //         active: false,
  //         children: [
  //           { path: '/pages/file-manager/filemanager', title: 'File Manager', type: 'link' },
  //           { path: '/pages/file-manager/filemanager-list', title: 'File Manager List', type: 'link' },
           
  //         ],
  //       },
  //       {
  //         title: 'Ecommerce',
  //         type: 'sub',
  //         Menusub: true,
  //         active: false,
  //         children: [
  //           {
  //             path: '/pages/ecommerce/shop',
  //             title: 'Shop',
  //             type: 'link',
  //           },
  //           {
  //             path: '/pages/ecommerce/product-details',
  //             title: 'Product Details',
  //             type: 'link',
  //           },
  //           { path: '/pages/ecommerce/shopping-cart', 
  //           title: 'Shopping Cart', 
  //           type: 'link' 
  //         },
  //         {
  //           path: '/pages/ecommerce/add-product',
  //           title: 'Add Product',
  //           type: 'link',
  //         },
  //         { path: '/pages/ecommerce/wishlist', 
  //         title: 'Wishlist',
  //          type: 'link'
  //          },
  //          { path: '/pages/ecommerce/checkout',
  //           title: 'CheckOut',
  //            type: 'link' },   
  //         ],
  //       },
     
  //     ],
    },
    {
     /*  title: 'MySQL',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" class="side-menu__icon" fill="#000000">
      <path d="M11 15h2v2h-2v-2zm0-8h2v6h-2V7zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z">
      </path>
  </svg>`,
      type: 'sub',
        type: 'link',
      Menusub: true,
      active: false,
     children: [
        {
          title: 'LogIn',
          Menusub: true,
          active: false,
           path: '/authentication/login',  type: 'link' 
          },

          {
            title: 'Register',
            Menusub: true,
            active: false,
             path: '/authentication/register',  type: 'link' 
            },
            {
              title: 'Forgot Password',
              Menusub: true,
              active: false,
               path: '/authentication/forgot-password',  type: 'link' 
              },
              {
                title: 'Lock Screen',
                Menusub: true,
                active: false,
                 path: '/authentication/lock-screen',  type: 'link' 
                },
                {
                  title: 'Under Maintenance',
                  Menusub: true,
                  active: false,
                   path: '/authentication/under-maintainance',  type: 'link' 
                  },
        
        {
          title: 'Error Pages',
          type: 'sub',
          Menusub: true,
          active: false,
          children: [
            { path: '/error-pages/error400', title: '400', type: 'link' },
            { path: '/error-pages/error401', title: '401', type: 'link' },
            { path: '/error-pages/error403', title: '403', type: 'link' },
            { path: '/error-pages/error404', title: '404', type: 'link' },
            { path: '/error-pages/error500', title: '500', type: 'link' },
            { path: '/error-pages/error503', title: '503', type: 'link' },
          ],
        },
     
      ],*/
    },

  //   {
  //     title: 'Data Source',
  //     type: 'sub',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000" class="side-menu__icon">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M8 16h8v2H8zm0-4h8v2H8zm6-10H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z">
  //     </path>
  // </svg>`,
  //     Menusub: true,
  //     active: false,
  //      children: [
  //       { path: 'workbench/work-bench', title: 'Form Elements', type: 'link' },
  //       { path: '/form-module/form-layouts', title: 'Form Layouts', type: 'link' },
  //       { path: '/form-module/form-advanced', title: 'Form Advanced', type: 'link' },
  //       { path: '/form-module/form-editor', title: 'Form Editor', type: 'link' },
  //       { path: '/form-module/form-validation', title: 'Form Validation', type: 'link' },
  //       { path: '/form-module/form-input-spinners', title: 'Form Input Spinners', type: 'link' },
  //       { path: '/form-module/select2', title: 'Select-2', type: 'link' },
  //       //  this.childrenss[0]

  //      ],
  //     //children:this.childrenss[0]
  //   },



    //Widgets
    {
      title: 'Home',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
      <path d="M0 0h24v24H0V0z" fill="none"></path>
      <path d="M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"></path>
  </svg>`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/home',
      type: 'link',
      nochild: true,
    },
    {
      title: 'Scheduling',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
      <path d="M0 0h24v24H0V0z" fill="none"></path>
      <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 21c0 1.1.89 2 1.99 2H19c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H5V8h14v13zM7 10h5v5H7z"></path>
      </svg>`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/scheduling',
      type: 'link',
      nochild: true,
    },
    // {
    //   title: 'Data Points',
    //   icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="side-menu__icon">
    //   <path d="M0 0h24v24H0V0z" fill="none"></path>
    //   <path d="M11.99 18.54l-7.37-5.73L3 14.07l9 7 9-7-1.63-1.27zM12 16l7.36-5.73L21 9l-9-7-9 7 1.63 1.27L12 16zm0-11.47L17.74 9 12 13.47 6.26 9 12 4.53z">
    //   </path>
    //   </svg>`,
    //   active: false,
    //   badgeClass: 'badge badge-sm bg-secondary badge-hide',
    //   badgeValue: 'new',
    //   path: '',
    //   type: 'link',
    //   nochild: true,
    // },
    {
      title: 'EasyConnect',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="side-menu__icon" width="10px" height="10px" viewBox="-1 -1 13 13" version="1.1">
<g id="surface1">
<path d="M 1.667969 3.332031 C 0.746094 3.332031 0 2.585938 0 1.667969 C 0 0.746094 0.746094 0 1.667969 0 C 2.585938 0 3.332031 0.746094 3.332031 1.667969 C 3.332031 2.585938 4.078125 3.332031 5 3.332031 C 5.921875 3.332031 6.667969 2.585938 6.667969 1.667969 C 6.667969 0.746094 7.414062 0 8.332031 0 C 9.253906 0 10 0.746094 10 1.667969 C 10 2.585938 9.253906 3.332031 8.332031 3.332031 C 5.570312 3.332031 3.332031 5.574219 3.332031 8.332031 C 3.332031 9.253906 2.585938 10 1.667969 10 C 0.746094 10 0 9.253906 0 8.332031 C 0 7.414062 0.746094 6.667969 1.667969 6.667969 C 2.585938 6.667969 3.332031 5.921875 3.332031 5 C 3.332031 4.078125 2.585938 3.332031 1.667969 3.332031 Z M 1.667969 3.332031 "/>
<path d="M 4.582031 7.292969 C 4.582031 5.796875 5.796875 4.582031 7.292969 4.582031 C 8.789062 4.582031 10 5.796875 10 7.292969 C 10 8.789062 8.789062 10 7.292969 10 C 5.796875 10 4.582031 8.789062 4.582031 7.292969 Z M 4.582031 7.292969 "/>
</g>
</svg>
`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/easyConnection',
      type: 'link',
      nochild: true, 
    },
//     {
//       title: 'DataDeck',
//       icon: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="side-menu__icon" width="10px" height="10px" viewBox="-1 -1 13 11" version="1.1">
// <g id="surface1">
// <path d="M 0 0.34375 C 0 0.152344 0.164062 0 0.367188 0 L 9.632812 0 C 9.835938 0 10 0.152344 10 0.34375 L 10 2.667969 L 0 2.667969 Z M 0 0.34375 "/>
// <path d="M 0 3.332031 L 10 3.332031 L 10 5.5 L 0 5.5 Z M 0 3.332031 "/>
// <path d="M 0 6.332031 L 10 6.332031 L 10 7.65625 C 10 7.847656 9.835938 8 9.632812 8 L 0.367188 8 C 0.164062 8 0 7.847656 0 7.65625 Z M 0 6.332031 "/>
// </g>
// </svg>`,
//       active: false,
//       badgeClass: 'badge badge-sm bg-secondary badge-hide',
//       badgeValue: 'new',
//       path: 'datamplify',
//       type: 'link',
//       nochild: true,
//     },
    {
      title: 'FlowBoard',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="side-menu__icon" width="10px" height="10px" viewBox="-1 -1 13 13" version="1.1">
<g id="surface1">
<path d="M 7.636719 6.171875 L 7.636719 5.292969 L 8.242188 5.292969 C 9.210938 5.292969 10 4.503906 10 3.535156 C 10 2.566406 9.210938 1.777344 8.242188 1.777344 L 7.636719 1.777344 L 7.636719 0.898438 L 2.363281 0.898438 L 2.363281 1.777344 L 1.777344 1.777344 L 1.777344 2.363281 L 2.363281 2.363281 L 2.363281 3.242188 L 7.636719 3.242188 L 7.636719 2.363281 L 8.242188 2.363281 C 8.886719 2.363281 9.414062 2.890625 9.414062 3.535156 C 9.414062 4.179688 8.886719 4.707031 8.242188 4.707031 L 7.636719 4.707031 L 7.636719 3.828125 L 2.363281 3.828125 L 2.363281 4.707031 L 1.757812 4.707031 C 0.789062 4.707031 0 5.496094 0 6.464844 C 0 7.433594 0.789062 8.222656 1.757812 8.222656 L 2.363281 8.222656 L 2.363281 9.101562 L 7.636719 9.101562 L 7.636719 8.222656 L 8.222656 8.222656 L 8.222656 7.636719 L 7.636719 7.636719 L 7.636719 6.757812 L 2.363281 6.757812 L 2.363281 7.636719 L 1.757812 7.636719 C 1.113281 7.636719 0.585938 7.109375 0.585938 6.464844 C 0.585938 5.820312 1.113281 5.292969 1.757812 5.292969 L 2.363281 5.292969 L 2.363281 6.171875 Z M 7.636719 6.171875 "/>
<path d="M 8.539062 7.34375 L 9.125 7.929688 L 8.539062 8.515625 L 8.953125 8.929688 L 10 7.929688 L 8.953125 6.929688 Z M 8.539062 7.34375 "/>
<path d="M 0.414062 3.070312 L 1.460938 2.070312 L 0.414062 1.070312 L 0 1.484375 L 0.585938 2.070312 L 0 2.65625 Z M 0.414062 3.070312 "/>
</g>
</svg>
`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/flowboardList',
      type: 'link',
      nochild: true,
    },
    {
      title: 'TaskPlan',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="side-menu__icon" width="10px" height="10px" viewBox="-1 -1 13 13" version="1.1">
<g id="surface1">
<path d="M 8.1875 0.9375 L 7.8125 0.9375 L 7.8125 0.625 C 7.8125 0.542969 7.78125 0.460938 7.722656 0.402344 C 7.664062 0.34375 7.582031 0.3125 7.5 0.3125 C 7.417969 0.3125 7.335938 0.34375 7.277344 0.402344 C 7.21875 0.460938 7.1875 0.542969 7.1875 0.625 L 7.1875 0.9375 L 5.3125 0.9375 L 5.3125 0.625 C 5.3125 0.542969 5.28125 0.460938 5.222656 0.402344 C 5.164062 0.34375 5.082031 0.3125 5 0.3125 C 4.917969 0.3125 4.835938 0.34375 4.777344 0.402344 C 4.71875 0.460938 4.6875 0.542969 4.6875 0.625 L 4.6875 0.9375 L 2.8125 0.9375 L 2.8125 0.625 C 2.8125 0.542969 2.78125 0.460938 2.722656 0.402344 C 2.664062 0.34375 2.582031 0.3125 2.5 0.3125 C 2.417969 0.3125 2.335938 0.34375 2.277344 0.402344 C 2.21875 0.460938 2.1875 0.542969 2.1875 0.625 L 2.1875 0.9375 L 1.8125 0.9375 C 1.496094 0.9375 1.195312 1.0625 0.972656 1.285156 C 0.75 1.507812 0.625 1.808594 0.625 2.125 L 0.625 8.5 C 0.625 8.816406 0.75 9.117188 0.972656 9.339844 C 1.195312 9.5625 1.496094 9.6875 1.8125 9.6875 L 8.1875 9.6875 C 8.503906 9.6875 8.804688 9.5625 9.027344 9.339844 C 9.25 9.117188 9.375 8.816406 9.375 8.5 L 9.375 2.125 C 9.375 1.808594 9.25 1.507812 9.027344 1.285156 C 8.804688 1.0625 8.503906 0.9375 8.1875 0.9375 Z M 4.28125 6.472656 L 3.34375 7.410156 C 3.285156 7.46875 3.207031 7.5 3.125 7.5 C 3.042969 7.5 2.960938 7.46875 2.902344 7.410156 L 2.277344 6.785156 C 2.25 6.753906 2.226562 6.71875 2.207031 6.683594 C 2.191406 6.644531 2.183594 6.601562 2.183594 6.5625 C 2.183594 6.519531 2.191406 6.480469 2.207031 6.441406 C 2.222656 6.402344 2.246094 6.367188 2.273438 6.335938 C 2.304688 6.308594 2.339844 6.285156 2.378906 6.269531 C 2.414062 6.253906 2.457031 6.246094 2.5 6.246094 C 2.539062 6.246094 2.582031 6.253906 2.621094 6.273438 C 2.65625 6.289062 2.691406 6.3125 2.71875 6.339844 L 3.125 6.746094 L 3.839844 6.027344 C 3.902344 5.972656 3.980469 5.941406 4.0625 5.941406 C 4.144531 5.941406 4.222656 5.976562 4.28125 6.03125 C 4.335938 6.089844 4.371094 6.167969 4.371094 6.25 C 4.371094 6.332031 4.339844 6.410156 4.28125 6.472656 Z M 4.28125 3.660156 L 3.34375 4.597656 C 3.285156 4.65625 3.207031 4.6875 3.125 4.6875 C 3.042969 4.6875 2.960938 4.65625 2.902344 4.597656 L 2.277344 3.972656 C 2.25 3.941406 2.226562 3.90625 2.207031 3.871094 C 2.191406 3.832031 2.183594 3.789062 2.183594 3.75 C 2.183594 3.707031 2.191406 3.667969 2.207031 3.628906 C 2.222656 3.589844 2.246094 3.554688 2.273438 3.523438 C 2.304688 3.496094 2.339844 3.472656 2.378906 3.457031 C 2.414062 3.441406 2.457031 3.433594 2.5 3.433594 C 2.539062 3.433594 2.582031 3.441406 2.621094 3.460938 C 2.65625 3.476562 2.691406 3.5 2.71875 3.527344 L 3.125 3.933594 L 3.839844 3.214844 C 3.902344 3.160156 3.980469 3.128906 4.0625 3.128906 C 4.144531 3.128906 4.222656 3.164062 4.28125 3.21875 C 4.335938 3.277344 4.371094 3.355469 4.371094 3.4375 C 4.371094 3.519531 4.339844 3.597656 4.28125 3.660156 Z M 7.5 7.1875 L 5.3125 7.1875 C 5.230469 7.1875 5.148438 7.15625 5.089844 7.097656 C 5.03125 7.039062 5 6.957031 5 6.875 C 5 6.792969 5.03125 6.710938 5.089844 6.652344 C 5.148438 6.59375 5.230469 6.5625 5.3125 6.5625 L 7.5 6.5625 C 7.582031 6.5625 7.664062 6.59375 7.722656 6.652344 C 7.78125 6.710938 7.8125 6.792969 7.8125 6.875 C 7.8125 6.957031 7.78125 7.039062 7.722656 7.097656 C 7.664062 7.15625 7.582031 7.1875 7.5 7.1875 Z M 7.5 4.375 L 5.3125 4.375 C 5.230469 4.375 5.148438 4.34375 5.089844 4.285156 C 5.03125 4.226562 5 4.144531 5 4.0625 C 5 3.980469 5.03125 3.898438 5.089844 3.839844 C 5.148438 3.78125 5.230469 3.75 5.3125 3.75 L 7.5 3.75 C 7.582031 3.75 7.664062 3.78125 7.722656 3.839844 C 7.78125 3.898438 7.8125 3.980469 7.8125 4.0625 C 7.8125 4.144531 7.78125 4.226562 7.722656 4.285156 C 7.664062 4.34375 7.582031 4.375 7.5 4.375 Z M 7.5 4.375 "/>
</g>
</svg`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/taskplanList',
      type: 'link',
      nochild: true,
    },
    {
      title: 'Monitoring',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="side-menu__icon" width="10px" height="10px" viewBox="-1 -1 13 13" version="1.1">
<g id="surface1">
<path d="M 3.453125 3.179688 C 2.832031 3.179688 2.328125 3.683594 2.328125 4.304688 C 2.328125 4.929688 2.832031 5.433594 3.453125 5.433594 C 4.078125 5.433594 4.582031 4.929688 4.582031 4.304688 C 4.582031 3.683594 4.078125 3.179688 3.453125 3.179688 Z M 3.453125 3.179688 "/>
<path d="M 9.640625 0.6875 L 0.359375 0.6875 C 0.160156 0.6875 0 0.847656 0 1.046875 L 0 6.796875 C 0 6.996094 0.160156 7.15625 0.359375 7.15625 L 0.527344 7.15625 L 2.132812 5.550781 C 2.171875 5.511719 2.175781 5.449219 2.140625 5.40625 C 1.878906 5.09375 1.726562 4.6875 1.742188 4.246094 C 1.773438 3.339844 2.515625 2.609375 3.421875 2.59375 C 4.394531 2.574219 5.191406 3.371094 5.167969 4.34375 C 5.148438 5.25 4.414062 5.992188 3.507812 6.019531 C 3.234375 6.027344 2.976562 5.972656 2.746094 5.867188 C 2.703125 5.847656 2.65625 5.855469 2.625 5.890625 L 1.355469 7.15625 L 9.640625 7.15625 C 9.839844 7.15625 10 6.992188 10 6.796875 L 10 1.046875 C 10 0.847656 9.839844 0.6875 9.640625 0.6875 Z M 6.214844 5.773438 C 6.214844 5.933594 6.085938 6.066406 5.921875 6.066406 C 5.761719 6.066406 5.628906 5.933594 5.628906 5.773438 L 5.628906 4.644531 C 5.628906 4.480469 5.761719 4.351562 5.921875 4.351562 C 6.085938 4.351562 6.214844 4.480469 6.214844 4.644531 Z M 7.132812 5.773438 C 7.132812 5.933594 7.003906 6.066406 6.839844 6.066406 C 6.679688 6.066406 6.546875 5.933594 6.546875 5.773438 L 6.546875 2.691406 C 6.546875 2.527344 6.679688 2.398438 6.839844 2.398438 C 7.003906 2.398438 7.132812 2.527344 7.132812 2.691406 Z M 8.066406 5.773438 C 8.066406 5.933594 7.933594 6.066406 7.773438 6.066406 C 7.609375 6.066406 7.480469 5.933594 7.480469 5.773438 L 7.480469 3.472656 C 7.480469 3.308594 7.609375 3.179688 7.773438 3.179688 C 7.933594 3.179688 8.066406 3.308594 8.066406 3.472656 Z M 9 5.773438 C 9 5.933594 8.867188 6.066406 8.707031 6.066406 C 8.542969 6.066406 8.414062 5.933594 8.414062 5.773438 L 8.414062 4.253906 C 8.414062 4.089844 8.542969 3.960938 8.707031 3.960938 C 8.867188 3.960938 9 4.089844 9 4.253906 Z M 9 5.773438 "/>
<path d="M 7.34375 8.75 C 6.886719 8.554688 6.417969 8.417969 5.933594 8.339844 L 5.933594 7.785156 C 5.933594 7.726562 5.882812 7.675781 5.824219 7.675781 L 4.175781 7.675781 C 4.117188 7.675781 4.066406 7.726562 4.066406 7.785156 L 4.066406 8.34375 C 3.585938 8.417969 3.117188 8.554688 2.664062 8.746094 C 2.519531 8.808594 2.441406 8.976562 2.5 9.125 C 2.558594 9.28125 2.734375 9.355469 2.886719 9.289062 C 3.558594 9 4.269531 8.855469 5 8.855469 L 5.007812 8.855469 C 5.730469 8.855469 6.445312 9 7.113281 9.289062 L 7.117188 9.289062 C 7.152344 9.304688 7.191406 9.3125 7.230469 9.3125 C 7.367188 9.3125 7.496094 9.21875 7.519531 9.066406 C 7.542969 8.933594 7.46875 8.804688 7.34375 8.75 Z M 7.34375 8.75 "/>
<path d="M 0.527344 7.15625 L 0.0898438 7.59375 C -0.0234375 7.710938 -0.0234375 7.894531 0.0898438 8.007812 C 0.148438 8.066406 0.222656 8.09375 0.296875 8.09375 C 0.371094 8.09375 0.445312 8.066406 0.503906 8.007812 L 1.355469 7.15625 Z M 0.527344 7.15625 "/>
</g>
</svg>
`,
      active: false,
      badgeClass: 'badge badge-sm bg-secondary badge-hide',
      badgeValue: 'new',
      path: 'datamplify/monitorList',
      type: 'link',
      nochild: true,
    },
  //   {
  //     title: 'ETL',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M11 7h6v2h-6zm0 4h6v2h-6zm0 4h6v2h-6zM7 7h2v2H7zm0 4h2v2H7zm0 4h2v2H7zM20.1 3H3.9c-.5 0-.9.4-.9.9v16.2c0 .4.4.9.9.9h16.2c.4 0 .9-.5.9-.9V3.9c0-.5-.5-.9-.9-.9zM19 19H5V5h14v14z">
  //     </path>
  // </svg>`,
  //     active: false,
  //     badgeClass: 'badge badge-sm bg-secondary badge-hide',
  //     badgeValue: 'new',
  //     path: 'datamplify/etlList',
  //     type: 'link',
  //     nochild: true,
  //   },
    //component


  //   {
  //     title: 'Drog & Drop',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" enable-background="new 0 0 24 24" viewBox="0 0 24 24" fill="#000000">
  //     <g>
  //         <rect fill="none" height="24" width="24"></rect>
  //     </g>
  //     <g>
  //         <g>
  //             <path d="M6,15c-0.83,0-1.58,0.34-2.12,0.88C2.7,17.06,2,22,2,22s4.94-0.7,6.12-1.88C8.66,19.58,9,18.83,9,18C9,16.34,7.66,15,6,15 z M6.71,18.71c-0.28,0.28-2.17,0.76-2.17,0.76s0.47-1.88,0.76-2.17C5.47,17.11,5.72,17,6,17c0.55,0,1,0.45,1,1 C7,18.28,6.89,18.53,6.71,18.71z M17.42,13.65L17.42,13.65c6.36-6.36,4.24-11.31,4.24-11.31s-4.95-2.12-11.31,4.24l-2.49-0.5 C7.21,5.95,6.53,6.16,6.05,6.63L2,10.69l5,2.14L11.17,17l2.14,5l4.05-4.05c0.47-0.47,0.68-1.15,0.55-1.81L17.42,13.65z M7.41,10.83L5.5,10.01l1.97-1.97l1.44,0.29C8.34,9.16,7.83,10.03,7.41,10.83z M13.99,18.5l-0.82-1.91 c0.8-0.42,1.67-0.93,2.49-1.5l0.29,1.44L13.99,18.5z M16,12.24c-1.32,1.32-3.38,2.4-4.04,2.73l-2.93-2.93 c0.32-0.65,1.4-2.71,2.73-4.04c4.68-4.68,8.23-3.99,8.23-3.99S20.68,7.56,16,12.24z M15,11c1.1,0,2-0.9,2-2s-0.9-2-2-2s-2,0.9-2,2 S13.9,11,15,11z"></path>
  //         </g>
  //     </g>
  // </svg>`,
  //     active: false,
  //     badgeClass: 'badge badge-sm bg-secondary badge-hide',
  //     badgeValue: 'new',
  //     path: '/widgets',
  //     type: 'link',
  //     nochild: true,
  //   },
  //   { headTitle: 'Files' },
  //   {
  //     title: 'Text File',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
  //     <g>
  //         <rect fill="none" height="24" width="24"></rect>
  //     </g>
  //     <g>
  //         <g>
  //             <path d="M12,2C6.48,2,2,6.48,2,12c0,5.52,4.48,10,10,10s10-4.48,10-10 C22,6.48,17.52,2,12,2z M12,20c-4.41,0-8-3.59-8-8c0-4.41,3.59-8,8-8s8,3.59,8,8C20,16.41,16.41,20,12,20z" fill-rule="evenodd"></path>
  //             <path d="M13.49,11.38c0.43-1.22,0.17-2.64-0.81-3.62c-1.11-1.11-2.79-1.3-4.1-0.59 l2.35,2.35l-1.41,1.41L7.17,8.58c-0.71,1.32-0.52,2.99,0.59,4.1c0.98,0.98,2.4,1.24,3.62,0.81l3.41,3.41c0.2,0.2,0.51,0.2,0.71,0 l1.4-1.4c0.2-0.2,0.2-0.51,0-0.71L13.49,11.38z" fill-rule="evenodd"></path>
  //         </g>
  //     </g>
  // </svg>`,
  
  //    // type: 'sub',
  //    // Menusub: true,
  //    type: 'link',
  //     active: false,
  //     /*children: [
  //       { path: '/uikit/alerts', title: 'Alerts', type: 'link' },
  //       { path: '/uikit/buttons', title: 'Buttons', type: 'link' },
  //       { path: '/uikit/colors', title: 'Colors', type: 'link' },
  //       { path: '/uikit/avatars', title: 'Avatars', type: 'link' },
  //       { path: '/uikit/dropdowns', title: 'Dropdowns', type: 'link' },
  //       { path: '/uikit/listgroup', title: 'Listgroup', type: 'link' },
  //       { path: '/uikit/tags', title: 'Tags', type: 'link' },
  //       { path: '/uikit/pagination', title: 'pagination', type: 'link' },
  //       { path: '/uikit/navigation', title: 'Navigation', type: 'link' },
  //       { path: '/uikit/typography', title: 'Typography', type: 'link' },
  //       { path: '/uikit/breadcrumbs', title: 'Breadcrumb', type: 'link' },
  //       { path: '/uikit/badges-pills', title: 'Badges/Pills', type: 'link' },
  //       { path: '/uikit/offcanvas', title: 'Offcanvas', type: 'link' },
  //       { path: '/uikit/toast', title: 'Toast', type: 'link' },
  //       { path: '/uikit/media-object', title: 'Media Object', type: 'link' },
  //       { path: '/uikit/scrollspy', title: 'Scrollspy', type: 'link' },
  //       { path: '/uikit/accordions', title: 'Accordions', type: 'link' },
  //       { path: '/uikit/tabs', title: 'Tabs', type: 'link' },
  //       { path: '/uikit/modal', title: 'Modal', type: 'link' },
  //       { path: '/uikit/tooltip-popover',title: 'Tooltip & popovers', type: 'link', },
  //       { path: '/uikit/progress', title: 'progress', type: 'link' },
  //       { path: '/uikit/carousels', title: 'Carousels', type: 'link' },
  //     ],*/
  //   },
  //   {
  //     title: 'Json File',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000" class="side-menu__icon">
  //     <g>
  //         <rect fill="none" height="24" width="24"></rect>
  //     </g>
  //     <g>
  //         <g></g>
  //         <g>
  //             <circle cx="15.5" cy="9.5" r="1.5"></circle>
  //             <circle cx="8.5" cy="9.5" r="1.5"></circle>
  //             <path d="M12,18c2.28,0,4.22-1.66,5-4H7C7.78,16.34,9.72,18,12,18z"></path>
  //             <path d="M11.99,2C6.47,2,2,6.48,2,12c0,5.52,4.47,10,9.99,10C17.52,22,22,17.52,22,12C22,6.48,17.52,2,11.99,2z M12,20 c-4.42,0-8-3.58-8-8c0-4.42,3.58-8,8-8s8,3.58,8,8C20,16.42,16.42,20,12,20z"></path>
  //         </g>
  //     </g>
  // </svg>`,
  //    // type: 'sub',
  //    // Menusub: true,
  //    type: 'link',
  //     active: false,
  //    /* children: [
  //       { path: '/icons/font-awesome-icons', title: 'Font Awesome Icons', type: 'link' },
  //       { path: '/icons/material-design-icons', title: 'Material Design Icons', type: 'link' },
  //       { path: '/icons/simple-line-icons', title: 'Simple Line Icons', type: 'link' },
  //       { path: '/icons/feather-icons', title: 'Feather Icons', type: 'link' },
  //       { path: '/icons/ionic-icons', title: 'Ionic Icons', type: 'link' },
  //       { path: '/icons/flag-icons', title: 'Flag Icons', type: 'link' },
  //       { path: '/icons/pe7-icons', title: 'Pe7 Icons', type: 'link' },
  //       { path: '/icons/typicon-icons', title: 'Typicon Icons', type: 'link' },
  //       { path: '/icons/weather-icons', title: 'Weather Icons', type: 'link' },
  //       { path: '/icons/bootstrap-icons', title: 'Bootstrap Icons', type: 'link' },
  //     ],*/
  //   },

  
    //Advanced
  //   {
  //     title: 'Excel File',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" viewBox="0 0 24 24">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M16.66 4.52l2.83 2.83-2.83 2.83-2.83-2.83 2.83-2.83M9 5v4H5V5h4m10 10v4h-4v-4h4M9 15v4H5v-4h4m7.66-13.31L11 7.34 16.66 13l5.66-5.66-5.66-5.65zM11 3H3v8h8V3zm10 10h-8v8h8v-8zm-10 0H3v8h8v-8z">
  //     </path>
  // </svg>`,
  //    // type: 'sub',
  //    // Menusub: true,
  //    type: 'link',
  //     active: false,
  //    /* children: [
  //       { path: '/adminui/card-design', title: 'Card Design', type: 'link' },
  //       { path: '/adminui/full-calendar', title: 'Full Calender', type: 'link' },
  //       { path: '/adminui/chat', title: 'Chat', type: 'link' },
  //       { path: '/adminui/notifications', title: 'Notifications', type: 'link' },
  //       { path: '/adminui/sweetalerts', title: 'Sweet alerts', type: 'link' },
  //       { path: '/adminui/range-slider', title: 'Range slider', type: 'link' },
  //       { path: '/adminui/content-scrollbar', title: 'Content Scrollbar', type: 'link' },
  //       { path: '/adminui/loaders', title: 'Loaders', type: 'link' },
  //       { path: '/adminui/rating', title: 'Rating', type: 'link' },
  //       { path: '/adminui/timeline', title: 'Timeline', type: 'link' },
  //       { path: '/adminui/treeview', title: 'Treeview', type: 'link' },
  //       { path: '/adminui/ribbons', title: 'Ribbons', type: 'link' },
  //       { path: '/adminui/swiperjs', title: 'SwiperJs', type: 'link' },
  //       { path: '/adminui/userlist', title: 'User List', type: 'link' },
  //       { path: '/adminui/search', title: 'Search', type: 'link' },  
  //     ],*/
  //   },
   /* {
      title: 'LandingPage',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" enable-background="new 0 0 24 24" viewBox="0 0 24 24" fill="#000000">
      <g>
          <rect fill="none" height="24" width="24"></rect>
      </g>
      <g>
          <g>
              <path d="M6,15c-0.83,0-1.58,0.34-2.12,0.88C2.7,17.06,2,22,2,22s4.94-0.7,6.12-1.88C8.66,19.58,9,18.83,9,18C9,16.34,7.66,15,6,15 z M6.71,18.71c-0.28,0.28-2.17,0.76-2.17,0.76s0.47-1.88,0.76-2.17C5.47,17.11,5.72,17,6,17c0.55,0,1,0.45,1,1 C7,18.28,6.89,18.53,6.71,18.71z M17.42,13.65L17.42,13.65c6.36-6.36,4.24-11.31,4.24-11.31s-4.95-2.12-11.31,4.24l-2.49-0.5 C7.21,5.95,6.53,6.16,6.05,6.63L2,10.69l5,2.14L11.17,17l2.14,5l4.05-4.05c0.47-0.47,0.68-1.15,0.55-1.81L17.42,13.65z M7.41,10.83L5.5,10.01l1.97-1.97l1.44,0.29C8.34,9.16,7.83,10.03,7.41,10.83z M13.99,18.5l-0.82-1.91 c0.8-0.42,1.67-0.93,2.49-1.5l0.29,1.44L13.99,18.5z M16,12.24c-1.32,1.32-3.38,2.4-4.04,2.73l-2.93-2.93 c0.32-0.65,1.4-2.71,2.73-4.04c4.68-4.68,8.23-3.99,8.23-3.99S20.68,7.56,16,12.24z M15,11c1.1,0,2-0.9,2-2s-0.9-2-2-2s-2,0.9-2,2 S13.9,11,15,11z"></path>
          </g>
      </g>
  </svg>`,
      type: 'link',
      active: false,
      path:"/landingpage"
    
    },
    {
      title: 'NestedMenu',
      icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">
      <path d="M0 0h24v24H0V0z" fill="none"></path>
      <path d="M11 7h6v2h-6zm0 4h6v2h-6zm0 4h6v2h-6zM7 7h2v2H7zm0 4h2v2H7zm0 4h2v2H7zM20.1 3H3.9c-.5 0-.9.4-.9.9v16.2c0 .4.4.9.9.9h16.2c.4 0 .9-.5.9-.9V3.9c0-.5-.5-.9-.9-.9zM19 19H5V5h14v14z">
      </path>
  </svg>`,
      type: 'sub',
      Menusub: false,
      active: false,
      children: [
        {
        
          title: 'Nested-1',
          type: 'empty',
          active: false,
        },
        {
          title: 'Nested-2',
          icon: 'database',
          type: 'sub',
          active: false,
          children: [
            {
            
              title: 'Nested-2-1',
              type: 'empty',
              active: false,
            },
            {
            
              title: 'Nested-2-2',
              type: 'empty',
              active: false,
            },
          ],
        },
      ],
    },*/
  //   { headTitle: 'FORMS & TABLES' },

  //   {
  //     title: 'Forms',
  //     type: 'sub',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000" class="side-menu__icon">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M8 16h8v2H8zm0-4h8v2H8zm6-10H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z">
  //     </path>
  // </svg>`,
  //     Menusub: true,
  //     active: false,
  //     children: [
  //       { path: '/form-module/form-elements', title: 'Form Elements', type: 'link' },
  //       { path: '/form-module/form-layouts', title: 'Form Layouts', type: 'link' },
  //       { path: '/form-module/form-advanced', title: 'Form Advanced', type: 'link' },
  //       { path: '/form-module/form-editor', title: 'Form Editor', type: 'link' },
  //       { path: '/form-module/form-validation', title: 'Form Validation', type: 'link' },
  //       { path: '/form-module/form-input-spinners', title: 'Form Input Spinners', type: 'link' },
  //       { path: '/form-module/select2', title: 'Select-2', type: 'link' },

  //     ],
  //   },
  //       {
  //         title: 'Tables',
  //         type: 'sub',
  //         icon: `<svg xmlns="http://www.w3.org/2000/svg" class="side-menu__icon" enable-background="new 0 0 24 24" viewBox="0 0 24 24" fill="#000000">
  //         <g>
  //             <rect fill="none" height="24" width="24"></rect>
  //         </g>
  //         <g>
  //             <g>
  //                 <g>
  //                     <path d="M3,3v8h8V3H3z M9,9H5V5h4V9z M3,13v8h8v-8H3z M9,19H5v-4h4V19z M13,3v8h8V3H13z M19,9h-4V5h4V9z M13,13v8h8v-8H13z M19,19h-4v-4h4V19z"></path>
  //                 </g>
  //             </g>
  //         </g>
  //     </svg>`,
  //         Menusub: true,
  //         active: false,
  //         children: [
  //           { path: '/tables/default-tables', title: 'Default Tables', type: 'link' },
  //           { path: '/tables/data-tables', title: 'Data Tables', type: 'link' },
  //           { path: '/tables/gridjs-tables', title: 'Grid Tables', type: 'link' },

  //         ],
  //       },
      
    

   

  //   { headTitle: 'MAPS & CHARTS' },
  //   {
  //     title: 'Maps',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000" class="side-menu__icon">
  //     <path d="M0 0h24v24H0z" fill="none"></path>
  //     <path d="M12 12c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm6-1.8C18 6.57 15.35 4 12 4s-6 2.57-6 6.2c0 2.34 1.95 5.44 6 9.14 4.05-3.7 6-6.8 6-9.14zM12 2c4.2 0 8 3.22 8 8.2 0 3.32-2.67 7.25-8 11.8-5.33-4.55-8-8.48-8-11.8C4 5.22 7.8 2 12 2z">
  //     </path>
  // </svg>`,
  //     type: 'sub',
  //     Menusub: true,
  //     active: false,
  //     children: [
  //       { path: '/maps/leaflet', title: 'Leaflet Maps', type: 'link' },
  //     ],
  //   },
  //   {
  //     title: 'Charts',
  //     icon: `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000" class="side-menu__icon">
  //     <path d="M0 0h24v24H0V0z" fill="none"></path>
  //     <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z">
  //     </path>
  // </svg>`,
  //     type: 'sub',
  //     Menusub: true,
  //     active: false,
  //     children: [
  //       { path: '/charts/apexcharts', title: 'Apexcharts', type: 'link' },
  //       { path: '/charts/chartjs', title: 'chartJs', type: 'link' },
  //       { path: '/charts/echarts', title: 'Echarts', type: 'link' },
  //     ],
  //   },
  
  
  ];
  // Array
  items = new BehaviorSubject<Menu[]>(this.MENUITEMS);
}
