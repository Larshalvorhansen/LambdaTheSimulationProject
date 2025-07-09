%% Calculate Root Mean Squared Error of ABM

clear;
year_=2010;
max_year=2019;
number_years=10;
number_quarters=4*number_years;
quarters_num=datenum(year_,4:3:number_years*12+1,0);
horizons=[1 2 4 8 12];
number_horizons=length(horizons);
number_variables=8;

forecast=NaN(number_quarters,number_horizons,number_variables);
actual=NaN(number_quarters,number_horizons,number_variables);

% Load data
load ../data/data/1996.mat
load ../data/ea/1996.mat

% Calculate gdp deflator growth from levels
data.gdp_deflator_growth_quarterly(2:end)=exp(diff(log(data.nominal_gdp_quarterly./data.real_gdp_quarterly)))-1;
ea.gdp_deflator_growth_quarterly(2:end)=exp(diff(log(ea.nominal_gdp_quarterly./ea.real_gdp_quarterly)))-1;

for i=1:number_quarters
    quarter_num=quarters_num(i);
    
    % Load data
    load(['../data/abm/',num2str(year(datetime(datestr(quarters_num(i))))),'Q',num2str(quarter(datetime(datestr(quarters_num(i))))),'.mat']);
    
    for j=1:number_horizons
        horizon=horizons(j);
        forecast_quarter_num=datenum(datetime(year(datetime(datestr(quarter_num))),month(datetime(datestr(quarter_num)))+(3*horizon)+1,0));
        
        if forecast_quarter_num>datenum(datetime(max_year,12,31))
            break
        end
        
        actual(i,j,:)=[log(data.real_gdp_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(1+data.gdp_deflator_growth_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(data.real_government_consumption_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(data.real_exports_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(data.real_imports_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(ea.real_gdp_quarterly(ea.quarters_num==forecast_quarter_num)) ...
            log(1+ea.gdp_deflator_growth_quarterly(ea.quarters_num==forecast_quarter_num)) ...
            (1+data.euribor(data.quarters_num==forecast_quarter_num)).^(1/4) ...
            ];
        
        forecast(i,j,:)=[log(mean(model.real_gdp_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(1+mean(model.gdp_deflator_growth_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(mean(model.real_government_consumption_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(mean(model.real_exports_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(mean(model.real_imports_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(mean(model.real_gdp_ea_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            log(1+mean(model.gdp_deflator_growth_ea_quarterly(model.quarters_num==forecast_quarter_num,:),2)) ...
            (1+mean(model.euribor(model.quarters_num==forecast_quarter_num,:),2)).^(1/4) ...
            ];
    end
end

save('forecast_validation_abm','forecast','actual');
rmse_validation_abm=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
bias_validation_abm=squeeze(nanmean(forecast-actual));
error_validation_abm=forecast-actual;

load('forecast_validation_var','forecast','actual');
rmse_validation_var=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
error_validation_var=forecast-actual;

% generate LaTex code error table
input.data=cellstr(string(round(100*(rmse_validation_var-rmse_validation_abm)./rmse_validation_var,1)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,p_value]=dmtest_modified(rmmissing(error_validation_var(:,j,l)),rmmissing(error_validation_abm(:,j,l)),h);
        input.data{j,l}=[input.data{j,l},' (',num2str(round(p_value,2),'%.2f'),stars(p_value),')'];
    end
end

% Set row labels (use empty string for no label):
input.tableRowLabels = {'1q','2q','4q','8q','12q'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('rmse_validation_abm.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

% generate LaTex code bias table
input.data=cellstr(string(round(bias_validation_abm,4)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,~,p_value]=mztest(rmmissing(actual(:,j,l)),rmmissing(error_validation_abm(:,j,l)+actual(:,j,l)));
        input.data{j,l}=[input.data{j,l},' (',num2str(round(p_value,2),'%.2f'),stars(p_value),')'];
    end
end

% Set row labels (use empty string for no label):
input.tableRowLabels = {'1q','2q','4q','8q','12q'};

% Formatting-string to set the precision of the table values:
input.dataFormat = {'%.2f'};

% Column alignment in Latex table ('l'=left-justified, 'c'=centered,'r'=right-justified):
input.tableColumnAlignment = 'r';

% Switch table borders on/off:
input.tableBorders = 0;

% Switch table booktabs on/off:
input.booktabs = 0;

% Switch to generate a complete LaTex document or just a table:
input.makeCompleteLatexDocument = 0;

latex = latexTableContent(input);

% save LaTex code as file
fid=fopen('bias_validation_abm.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);
