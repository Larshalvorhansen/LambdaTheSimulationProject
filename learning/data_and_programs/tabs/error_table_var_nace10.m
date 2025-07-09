%% Calculate Root Mean Squared Error of VAR

clear;
year_=2010;
max_year=2019;
number_years=10;
number_quarters=4*number_years;
quarters_num=datenum(year_,4:3:number_years*12+1,0);
horizons=[1 2 4 8 12];
number_horizons=length(horizons);
number_variables=10;
presample=4;

forecast=NaN(number_quarters,number_horizons,number_variables);
actual=NaN(number_quarters,number_horizons,number_variables);

% Load data
load('../data/data/1996.mat');

for k=1:3
for i=1:number_quarters
    quarter_num=quarters_num(i);
    
    for j=1:number_horizons
        horizon=horizons(j);
        forecast_quarter_num=datenum(datetime(year(datetime(datestr(quarter_num))),month(datetime(datestr(quarter_num)))+(3*horizon)+1,0));
        
        if forecast_quarter_num>datenum(datetime(max_year,12,31))
            break
        end
        
        actual(i,j,:)=log(data.nominal_nace10_gva_quarterly(data.quarters_num==forecast_quarter_num,:));
        
        Y0=log(data.nominal_nace10_gva_quarterly(data.quarters_num<=quarter_num,:));

        Y=forecast_var(diff(Y0(presample-k:end,:),1),horizon,k);
        Y(end,:)=Y0(end,:)+sum(Y,1);
        forecast(i,j,:)=Y(end,:);
    end
end

if k==1
    save('forecast_var_nace10','forecast','actual');
    rmse_var_nace10=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    bias_var_nace10=squeeze(nanmean(forecast-actual));
    error_var_nace10=forecast-actual;
else
    save(['forecast_var_nace10','_',num2str(k)],'forecast','actual');
    rmse_var_nace10_k=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    bias_var_nace10_k=squeeze(nanmean(forecast-actual));
    error_var_nace10_k=forecast-actual;
    
    load('forecast_var_nace10','forecast','actual');
    rmse_var_nace10=100*squeeze(sqrt(nanmean((forecast-actual).^2)));
    error_var_nace10=forecast-actual;
end

% generate LaTex code error table
if k==1
    input.data=cellstr(string(round(rmse_var_nace10,2)));
else
input.data=cellstr(string(round(100*(rmse_var_nace10-rmse_var_nace10_k)./rmse_var_nace10,1)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,p_value]=dmtest_modified(rmmissing(error_var_nace10(:,j,l)),rmmissing(error_var_nace10_k(:,j,l)),h);
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
    fid=fopen('rmse_var_nace10.tex','w');
else
    fid=fopen(['rmse_var_nace10','_',num2str(k),'.tex'],'w');
end

[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);

if k==1
% generate LaTex code bias table
input.data=cellstr(string(round(bias_var_nace10,4)));

for j=1:length(horizons)
    h=horizons(j);
    for l=1:number_variables
        [~,~,p_value]=mztest(rmmissing(actual(:,j,l)),rmmissing(error_var_nace10(:,j,l)+actual(:,j,l)));
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
fid=fopen('bias_var_nace10.tex','w');
[nrows,ncols] = size(latex);
for row = 1:nrows
    fprintf(fid,'%s\n',latex{row,:});
end
fclose(fid);
end
end
