/*
 * Copyright (c) by CryptoLab inc.
 * This program is licensed under a
 * Creative Commons Attribution-NonCommercial 3.0 Unported License.
 * You should have received a copy of the license along with this
 * work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.
 */

#include "../src/HEAAN.h"

using namespace std;
using namespace NTL;


int main() {
    TestScheme::testLogarithmBatch(13, 155, 30, 7, 3);
    return 0;
}
