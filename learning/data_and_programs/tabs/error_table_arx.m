%% Calculate Root Mean Squared Error of ARX

clear;
year_=2010;
max_year=2019;
number_years=10;
number_quarters=4*number_years;
quarters_num=datenum(year_,4:3:number_years*12+1,0);
horizons=[1 2 4 8 12];
number_horizons=length(horizons);
number_variables=4;
presample=4;

forecast=NaN(number_quarters,number_horizons,number_variables);
actual=NaN(number_quarters,number_horizons,number_variables);

% Load data
load('../data/data/1996.mat');

% Calculate gdp deflator from levels
data.gdp_deflator_growth_quarterly(2:end)=exp(diff(log(data.nominal_gdp_quarterly./data.real_gdp_quarterly)))-1;
data.gdp_deflator_quarterly=data.nominal_gdp_quarterly./data.real_gdp_quarterly;

for k=1:3
for i=1:number_quarters
    quarter_num=quarters_num(i);
    
    for j=1:number_horizons
        horizon=horizons(j);
        forecast_quarter_num=datenum(datetime(year(datetime(datestr(quarter_num))),month(datetime(datestr(quarter_num)))+(3*horizon)+1,0));
        
        if forecast_quarter_num>datenum(datetime(max_year,12,31))
            break
        end
        
        actual(i,j,:)=[log(data.real_gdp_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(1+data.gdp_deflator_growth_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(data.real_household_consumption_quarterly(data.quarters_num==forecast_quarter_num)) ...
            log(data.real_fixed_capitalformation_quarterly(data.quarters_num==forecast_quarter_num)) ...
            ];
        
        X=[log(data.real_exports_quarterly) ...
            log(data.real_imports_quarterly) ...
            log(data.real_government_consumption_quarterly) ...
            ];
        
        Y0=[log(data.real_gdp_quarterly(data.quarters_num<=quarter_num)) ...
            log(data.gdp_deflator_quarterly(data.quarters_num<=quarter_num)) ...
            log(data.real_household_consumption_quarterly(data.quarters_num<=quarter_num)) ...
            log(data.real_fixed_capitalformation_quarterly(data.quarters_num<=quarter_num)) ...
            cumsum(log(1+(1+data.euribor(data.quarters_num<=quarter_num)).^(1/4)-1)) ...
            ];
        
        Y=zeros(horizon,number_variables);
        for l=1:number_variables
            Y(:,l)=forecast_varx(diff(Y0(presample-k:end,l),1),horizon,diff(X(presample-k:end,:),1),k);
        end
        Y(end,[1 3 4])=Y0(end,[1 3 4])+sum(Y(:,[1 3 4]),1);
        forecast(i,j,:)=Y(end,:);
    end
end

if k==1
    save('forecast_arx','forecast','actual');
    rmse_arx=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    bias_arx=squeeze(nanmean(forecast-actual));
    error_arx=forecast-actual;
else
    save(['forecast_arx','_',num2str(k)],'forecast','actual');
    rmse_arx_k=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    bias_arx_k=squeeze(nanmean(forecast-actual));
    error_arx_k=forecast-actual;
    
    load('forecast_arx','forecast','actual');
    rmse_arx=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    error_arx=forecast-actual;
end

% generate LaTex code error table
if k==1
    input.data=cellstr(string(round(rmse_arx,2)));
else
input.data=cellstr(string(round(100*(rmse_arx-rmse_arx_k)./rmse_arx,1)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,p_value]=dmtest_modified(rmmissing(error_arx(:,j,l)),rmmissing(error_arx_k(:,j,l)),h);
        input.data{j,l}=[input.data{j,l},' (',num2str(round(p_value,2),'%.2f'),stars(p_value),')'];
    end
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
if k==1
    fid=fopen('rmse_arx.tex','w');
else
    fid=fopen(['rmse_arx','_',num2str(k),'.tex'],'w');
end

[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

if k==1
% generate LaTex code bias table
input.data=cellstr(string(round(bias_arx,4)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,~,p_value]=mztest(rmmissing(actual(:,j,l)),rmmissing(error_arx(:,j,l)+actual(:,j,l)));
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
fid=fopen('bias_arx.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);
end
end
