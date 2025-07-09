load ../data/abm/2010Q4.mat
load ../data/data/1996.mat

year=2010;
number_years=3;

% calculate serial date numbers
years_num=datenum(year+1,1:12:number_years*12+1,0);

figure
ax=subplot(1,3,1,'align');
production_approach=[squeeze(mean(model.nominal_nace10_gva,2)),mean(model.nominal_gdp-model.nominal_gva,2)];
C=linspecer(size(production_approach,2),'grey');
ax.NextPlot='replacechildren';
ax.ColorOrder=C;
area(model.years_num,1e6*production_approach,'EdgeColor','none');
production_approach=[data.nominal_nace10_gva,mean(data.nominal_gdp-data.nominal_gva,2)];
hold
plot(data.years_num,1e6*cumsum(production_approach'),'k--')
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
h = legend(h,'A','B, C, D and E','F','G, H and I','J','K','L','M and N','O, P and Q','R and S','Taxes less subsidies','Location','southeast');
% h.Box = 'off';
title('Production approach');

ax=subplot(1,3,2,'align');
income_approach=[mean(model.wages,2),mean(model.compensation_employees,2)-mean(model.wages,2),mean(model.operating_surplus,2), mean(model.nominal_gva-model.compensation_employees-model.operating_surplus,2),mean(model.nominal_gdp-model.nominal_gva,2)];
C=linspecer(size(income_approach,2),'blue');
ax.NextPlot='replacechildren';
ax.ColorOrder=C;
area(model.years_num,1e6*income_approach,'EdgeColor','none');
income_approach=[mean(data.wages,2),mean(data.compensation_employees,2)-mean(data.wages,2),mean(data.operating_surplus,2), mean(data.nominal_gva-data.compensation_employees-data.operating_surplus,2),mean(data.nominal_gdp-data.nominal_gva,2)];
hold
plot(data.years_num,1e6*cumsum(income_approach'),'k--')
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
h = legend(h,'Wages','Social contributions','Gross operating surplus','Taxes less subsidies on production','Taxes less subsidies on products','Location','southeast');
% h.Box = 'off';
title('Income approach');

ax=subplot(1,3,3,'align');
expenditure_approach=[mean(model.nominal_household_consumption,2),mean(model.nominal_government_consumption,2), mean(model.nominal_capitalformation,2), mean(model.nominal_exports-model.nominal_imports,2)];
C=linspecer(size(expenditure_approach,2),'red');
ax.NextPlot='replacechildren';
ax.ColorOrder=C;
area(model.years_num,1e6*expenditure_approach,'EdgeColor','none');
expenditure_approach=[mean(data.nominal_household_consumption,2),mean(data.nominal_government_consumption,2), mean(data.nominal_capitalformation,2), mean(data.nominal_exports-data.nominal_imports,2)];
hold
plot(data.years_num,1e6*cumsum(expenditure_approach'),'k--')
h = gca;
h.XTick = years_num;
datetick('x','yyyy','keepticks');
grid on
h = legend(h,'Household consumption','Government consumption','Capital formation','Net exports','Location','southeast');
% h.Box = 'off';
title('Expenditure approach');

set(gcf, 'color', 'none','inverthardcopy', 'off', 'Renderer', 'painters');
set(gcf, 'Position', [0, 0, 933, 933*1/2]);
set(gcf,'PaperOrientation','landscape', 'PaperType', 'a0');
saveas(gcf,'national_accounting_comparison.pdf','pdf');
