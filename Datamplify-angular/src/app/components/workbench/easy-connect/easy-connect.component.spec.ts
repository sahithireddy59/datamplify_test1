import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EasyConnectComponent } from './easy-connect.component';

describe('EasyConnectComponent', () => {
  let component: EasyConnectComponent;
  let fixture: ComponentFixture<EasyConnectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EasyConnectComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EasyConnectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
