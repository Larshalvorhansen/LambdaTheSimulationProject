%%
%%
%% Generate Figures
%%
%%
%%

load ../data/data/1996.mat
load ../data/dsgex/2010Q4.mat
load ../data/arx/2010Q4.mat
load ../data/abmx/2010Q4.mat

N=64;
year=2010;
number_years=3;

% calculate serial date numbers
years_num=datenum(year+1,1:12:number_years*12+1,0);
quarters_num=datenum(year,4:3:(number_years+1)*12+1,0);

C=linspecer(2);

gdp_fig=figure;

% GDP real
subplot(2,3,1,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_gdp,2)',1e6*ci(model.real_gdp',[.9 .1])','k') %abs(1e6*quantile(model.real_gdp',[.9 .1])-1e6*mean(model.real_gdp,2)')
shadedErrorBar(dsgex.years_num',1e6*mean(dsgex.real_gdp,2)',1e6*flip(abs(dsgex.error_real_gdp'-dsgex.real_gdp')),'r') %flip(abs(dsgex.error_real_gdp'-dsgex.real_gdp'))
shadedErrorBar(arx.years_num',1e6*mean(arx.real_gdp,2)',1e6*ci(arx.real_gdp',[.9 .1])','b')
plot(data.years_num,1e6*data.real_gdp','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
h = findobj(gca,'Type','line');
h([3:4,6:7])=[];
h = legend(h,'DATA','AR(1)','DSGE','ABM','Location','best');
h.Box = 'off';
title('GDP (annual)');

% household_consumption real
subplot(2,3,2,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_household_consumption,2)',1e6*ci(model.real_household_consumption',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',1e6*mean(dsgex.real_household_consumption,2)',1e6*flip(abs(dsgex.error_real_household_consumption'-dsgex.real_household_consumption')),'r')
shadedErrorBar(arx.years_num',1e6*mean(arx.real_household_consumption,2)',1e6*ci(arx.real_household_consumption',[.9 .1])','b')
plot(data.years_num,1e6*data.real_household_consumption','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Consumption (annual)');

% fixed_capitalformation real
subplot(2,3,3,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_fixed_capitalformation,2)',1e6*ci(model.real_fixed_capitalformation',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',1e6*mean(dsgex.real_fixed_capitalformation,2)',1e6*flip(abs(dsgex.error_real_fixed_capitalformation'-dsgex.real_fixed_capitalformation')),'r')
shadedErrorBar(arx.years_num',1e6*mean(arx.real_fixed_capitalformation,2)',1e6*ci(arx.real_fixed_capitalformation',[.9 .1])','b')
plot(data.years_num,1e6*data.real_fixed_capitalformation','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Investment (annual)');

% government spending
subplot(2,3,4,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_government_consumption,2)',1e6*ci(model.real_government_consumption',[.9 .1])','k')
plot(data.years_num,1e6*data.real_government_consumption','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Government (annual)');

% exports
subplot(2,3,5,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_exports,2)',1e6*ci(model.real_exports',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',1e6*mean(dsgex.real_exports,2)',1e6*flip(abs(dsgex.error_real_exports'-dsgex.real_exports')),'r')
plot(data.years_num,1e6*data.real_exports','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Exports (annual)');

% imports
subplot(2,3,6,'align')
hold;
shadedErrorBar(model.years_num',1e6*mean(model.real_imports,2)',1e6*ci(model.real_imports',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',1e6*mean(dsgex.real_imports,2)',1e6*flip(abs(dsgex.error_real_imports'-dsgex.real_imports')),'r')
plot(data.years_num,1e6*data.real_imports','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Imports (annual)');

set(gdp_fig, 'color', 'none','inverthardcopy', 'off', 'Renderer', 'painters');
set(gdp_fig, 'Position', [0, 0, 1120*3/4, 1120*3/8], 'PaperOrientation', 'landscape')
saveas(gdp_fig,'out-of-sample-with-predictors.pdf','pdf');

gdp_fig=figure;

% GDP real
subplot(2,3,1,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_gdp_quarterly,2)',1e6*ci(model.real_gdp_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',1e6*mean(dsgex.real_gdp_quarterly,2)',1e6*flip(abs(dsgex.error_real_gdp_quarterly'-dsgex.real_gdp_quarterly')),'r')
shadedErrorBar(arx.quarters_num',1e6*mean(arx.real_gdp_quarterly,2)',1e6*ci(arx.real_gdp_quarterly',[.9 .1])','b')
plot(data.quarters_num,1e6*data.real_gdp_quarterly','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
h = findobj(gca,'Type','line');
h([3:4,6:7])=[];
h = legend(h,'DATA','AR(1)','DSGE','ABM','Location','best');
h.Box = 'off';
title('GDP (quarterly)');

% household_consumption real
subplot(2,3,2,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_household_consumption_quarterly,2)',1e6*ci(model.real_household_consumption_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',1e6*mean(dsgex.real_household_consumption_quarterly,2)',1e6*flip(abs(dsgex.error_real_household_consumption_quarterly'-dsgex.real_household_consumption_quarterly')),'r')
shadedErrorBar(arx.quarters_num',1e6*mean(arx.real_household_consumption_quarterly,2)',1e6*ci(arx.real_household_consumption_quarterly',[.9 .1])','b')
plot(data.quarters_num,1e6*data.real_household_consumption_quarterly','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Consumption (quarterly)');

% fixed_capitalformation real
subplot(2,3,3,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_fixed_capitalformation_quarterly,2)',1e6*ci(model.real_fixed_capitalformation_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',1e6*mean(dsgex.real_fixed_capitalformation_quarterly,2)',1e6*flip(abs(dsgex.error_real_fixed_capitalformation_quarterly'-dsgex.real_fixed_capitalformation_quarterly')),'r')
shadedErrorBar(arx.quarters_num',1e6*mean(arx.real_fixed_capitalformation_quarterly,2)',1e6*ci(arx.real_fixed_capitalformation_quarterly',[.9 .1])','b')
plot(data.quarters_num,1e6*data.real_fixed_capitalformation_quarterly','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Investment (quarterly)');

% government spending
subplot(2,3,4,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_government_consumption_quarterly,2)',1e6*ci(model.real_government_consumption_quarterly',[.9 .1])','k')
plot(data.quarters_num,1e6*data.real_government_consumption_quarterly','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Government (quarterly)');

% exports
subplot(2,3,5,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_exports_quarterly,2)',1e6*ci(model.real_exports_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',1e6*mean(dsgex.real_exports_quarterly,2)',1e6*flip(abs(dsgex.error_real_exports_quarterly'-dsgex.real_exports_quarterly')),'r')
plot(data.quarters_num,1e6*data.real_exports_quarterly','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Exports (quarterly)');

% imports
subplot(2,3,6,'align')
hold;
shadedErrorBar(model.quarters_num',1e6*mean(model.real_imports_quarterly,2)',1e6*ci(model.real_imports_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',1e6*mean(dsgex.real_imports_quarterly,2)',1e6*flip(abs(dsgex.error_real_imports_quarterly'-dsgex.real_imports_quarterly')),'r')
plot(data.quarters_num,1e6*data.real_imports_quarterly','--k');
h = gca;
%h.FontSize=13;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Imports (quarterly)');

set(gdp_fig, 'color', 'none','inverthardcopy', 'off', 'Renderer', 'painters');
set(gdp_fig, 'Position', [0, 0, 1120*3/4, 1120*3/8], 'PaperOrientation', 'landscape')
saveas(gdp_fig,'out-of-sample-with-predictors_quarterly.pdf','pdf');

gdp_fig=figure;

% GDP growth real
subplot(2,2,1,'align')
hold;
shadedErrorBar(model.years_num',100*mean(model.real_gdp_growth,2)',100*ci(model.real_gdp_growth',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',100*mean(dsgex.real_gdp_growth,2)',100*flip(abs(dsgex.error_real_gdp_growth'-dsgex.real_gdp_growth')),'r')
shadedErrorBar(arx.years_num',100*mean(arx.real_gdp_growth,2)',100*ci(arx.real_gdp_growth',[.9 .1])','b')
plot(data.years_num,100*data.real_gdp_growth','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
h = findobj(gca,'Type','line');
h([3:4,6:7])=[];
h = legend(h,'DATA','AR(1)','DSGE','ABM','Location','best');
h.Box = 'off';
grid on
title('GDP growth (annual)');

% Inflation
subplot(2,2,2,'align')
hold;
shadedErrorBar(model.years_num',100*mean(model.gdp_deflator_growth,2)',100*ci(model.gdp_deflator_growth',[.9 .1])','k')
shadedErrorBar(dsgex.years_num',100*mean(dsgex.gdp_deflator_growth,2)',100*flip(abs(dsgex.error_gdp_deflator_growth'-dsgex.gdp_deflator_growth')),'r')
shadedErrorBar(arx.years_num',100*mean(arx.gdp_deflator_growth,2)',100*ci(arx.gdp_deflator_growth',[.9 .1])','b')
plot(data.years_num,100*data.gdp_deflator_growth','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Inflation (annual)');

% GDP growth real
subplot(2,2,3,'align')
hold;
shadedErrorBar(model.quarters_num',100*mean(model.real_gdp_growth_quarterly,2)',100*ci(model.real_gdp_growth_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',100*mean(dsgex.real_gdp_growth_quarterly,2)',100*flip(abs(dsgex.error_real_gdp_growth_quarterly'-dsgex.real_gdp_growth_quarterly')),'r')
shadedErrorBar(arx.quarters_num',100*mean(arx.real_gdp_growth_quarterly,2)',100*ci(arx.real_gdp_growth_quarterly',[.9 .1])','b')
plot(data.quarters_num,100*data.real_gdp_growth_quarterly','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('GDP growth (quarterly)');

% Inflation
subplot(2,2,4,'align')
hold;
shadedErrorBar(model.quarters_num',100*mean(model.gdp_deflator_growth_quarterly,2)',100*ci(model.gdp_deflator_growth_quarterly',[.9 .1])','k')
shadedErrorBar(dsgex.quarters_num',100*mean(dsgex.gdp_deflator_growth_quarterly,2)',100*flip(abs(dsgex.error_gdp_deflator_growth_quarterly'-dsgex.gdp_deflator_growth_quarterly')),'r')
shadedErrorBar(arx.quarters_num',100*mean(arx.gdp_deflator_growth_quarterly,2)',100*ci(arx.gdp_deflator_growth_quarterly',[.9 .1])','b')
plot(data.quarters_num,100*data.gdp_deflator_growth_quarterly','--k');
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
title('Inflation (quarterly)');

set(gdp_fig, 'color', 'none','inverthardcopy', 'off', 'Renderer', 'painters');
saveas(gdp_fig,'out-of-sample-with-predictors_growth.pdf','pdf');
