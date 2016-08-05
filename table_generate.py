
from pyexcel_ods import ODSBook


def skip_comments(f):
    '''
    Read lines that DO NOT start with a # symbol.
    '''
    for line in f:
        if not line.strip().startswith('#'):
            yield line


def get_asteca_data():
    '''
    Read the ASteCA output data file 'asteca_output.dat' and store each
    data column for each cluster.
    '''

    # Path to data file.
    out_file = '../mc-catalog/asteca_output_final.dat'

    # Read data file
    with open(out_file) as f:
        as_names, as_pars = [], []

        for line in skip_comments(f):
            as_names.append(line.split()[0])
            # Read clusters met, age, and mass obtained by ASteCA.
            l = line.split()[1:]
            as_pars.append([l[19], l[21], l[27]])

    return as_names, as_pars


def d_search(dat_lst, cl_name, name_idx):
    '''
    Search the list of lists obtained when reading the .ods file, for the
    index of the list that contains a given cluster.
    '''
    for i, line in enumerate(dat_lst):
        if cl_name == line[name_idx]:
            return i
    return None


def get_liter_data(as_names):
    '''
    Read the data file with the literature values for each cluster as a
    dictionary.
    '''
    # Read .ods file with literature data.
    cl_file = ODSBook('../mc-catalog/lit_OCs_data.ods')
    # Store as dictionary and then as list.
    cl_dict = cl_file.sheets()["S-LMC"]

    # Indexes of RA,DEC in .ods literature file.
    ra_i, dec_i = cl_dict[0].index(u'ra_deg'), cl_dict[0].index(u'dec_deg')
    gal_i = cl_dict[0].index(u'Galaxia')
    # Column number for the cluster's name in the .ods file.
    name_idx = cl_dict[0].index(u'Name')
    oth_names = cl_dict[0].index(u'Names (Bica Table 3)')

    gal, lit_names, ra_dec = [], [], []
    for cl_name in as_names:
        cl_i = d_search(cl_dict, cl_name, name_idx)
        if cl_i is None:
            print 'WARNING: {} not found in ods file.'.format(cl_name)
        else:
            # Store data.
            gal.append(cl_dict[cl_i][gal_i])
            ra_dec.append([cl_dict[cl_i][ra_i], cl_dict[cl_i][dec_i]])
            if cl_dict[cl_i][oth_names] == '--':
                lit_names.append(cl_name)
            else:
                lit_names.append(cl_dict[cl_i][oth_names])

    return gal, lit_names, ra_dec


def print_data(as_names, as_pars, gal, lit_names, ra_dec):
    """
    Print data to file.
    """
    # Order lists according to RA values.
    o_ra_dec, o_gal, o_as_names, o_lit_names, o_as_pars =\
        map(list, zip(*sorted(zip(ra_dec, gal, as_names, lit_names,
                                  as_pars), reverse=False)))

    with open('test.md', "w") as f_out:

        f_out.write("| Gal  | Names  | (RA, DEC) (J2000)  | [Fe/H] |"
                    " log(age) | Mass (Mo)\n|---|---|---|---|---|---|\n")

        simbad = []
        for i, d in enumerate(zip(*[o_gal, o_as_names, o_lit_names, o_ra_dec,
                                    o_as_pars])):
            print d
            g, n, on, r, d, m, a, ma = d[0], d[1], d[2],\
                str(round(d[3][0], 5)), str(round(d[3][1], 5)),\
                d[4][0], d[4][1], d[4][2]
            # Link to Simbad
            s = "[{}]: http://simbad.u-strasbg.fr/simbad/sim-coo?".format(i) +\
                "Coord={}d+{}d&CooFrame=FK5&CooEpoch=2000&Coo".format(r, d) +\
                "Equi=2000&CooDefinedFrames=none&Radius=10&" +\
                "Radius.unit=arcsec&submit=submit+query&CoordList="
            simbad.append(s)

            f_out.write("| {} | [{}](/mc_asteca_img_all/{}.png)"
                        " | [{}, {}][{}] | {} | {} | {} |\n".format(
                            g, on, n, r, d, i, m, a, ma))
        f_out.write("\n\n")

    with open('test.md', "a") as f_out:
        for s in simbad:
            f_out.write("{}\n".format(s))


def main():
    '''
    Generate table in README.md file.
    '''
    # Read names, metallicities, ages and mass from 'asteca_output_final.dat'
    # file.
    as_names, as_pars = get_asteca_data()

    # Read .ods file
    gal, lit_names, ra_dec = get_liter_data(as_names)

    # Print to README.md file.
    print_data(as_names, as_pars, gal, lit_names, ra_dec)

    print '\nEnd.'


if __name__ == "__main__":
    main()
